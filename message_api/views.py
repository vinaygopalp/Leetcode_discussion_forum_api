from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import Message_serializer,ChatRoom_serializer,User_serializer,Contest_serializer,template_contest_ser,admin_contest_Ser
from chat.models import Message,ChatRoom,User_base as User
from django.shortcuts import redirect
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os 
import sys
import pika
from datetime import date, time, datetime
import requests
import threading
import asyncio
 
 
template_list = []
sorted_list = []
@api_view(['GET', 'POST','DELETE'])
def get_message(request):
    if request.method == "GET":
        messages = Message.objects.all()
        serializer = Message_serializer(messages, many=True) 
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = Message_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors":serializer.errors})
    elif request.method == "DELETE":
        message = Message.objects.get(id=request.data["id"])
        message.delete()
        return Response({"message":"Message Deleted"})
    

@api_view(['GET','POST','DELETE'])
def add_room(request):
    if request.method == "GET":
        rooms = ChatRoom.objects.all()
        serializer = ChatRoom_serializer(rooms, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ChatRoom_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors":serializer.errors})
    elif request.method == "DELETE":
        room = ChatRoom.objects.get(id=request.data["id"])
        room.delete()
        return Response({"message":"Room Deleted"})

@api_view(['GET','POST','DELETE'])
def add_user(request):
    if request.method == "GET":
        users = User.objects.all()
        serializer = User_serializer(users, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = User_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors":serializer.errors})
    elif request.method == "DELETE":
        user = User.objects.get(id=request.data["id"])
        user.delete()
        return Response({"message":"User Deleted"})

@api_view(['POST'])
def compexlity_analysis(request):
    if request.method == "POST":
        client = OpenAI(
        api_key = os.getenv("OPENAI_API_KEY")
        )
        data = request.data["code"]
        completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content":data + "need bigo time and space comp .dont include /// in your response message and also just the coplexity no extra message first time then space with a space"}
        ]
        )

        message_response=completion.choices[0].message.content
        
        return Response({"message":{
            "time complexity":message_response.split()[0],
            "space complexity":message_response.split()[1]
        }})

 

actual_start={}
@api_view(['POST','GET'])
def contest_start(request):
    
    if request.method == "POST" :
        global actual_start
        actual_start = {}
        actual_start = request.data
        print(actual_start)

        data = request.data
        return Response(data)
    if request.method == "GET":
        return Response(actual_start) 


 
contests_to_start = []

async def check_contests():
    global template_list
    global sorted_list
    """Background task to check if any contest should start."""
    while True:
        current_date = datetime.now().date()
        current_time = datetime.now().time().replace(microsecond=0)
        print(f"Checking contests at {current_date} {current_time}")
        
        for contest in contests_to_start[:]: 
            if isinstance(contest, list):  
                contest = contest[0]   
            start_date = contest["start_date"]
            start_time = contest["start_time"]
            print(start_date,start_time)
            if start_date <= str(current_date) and start_time <= str(current_time):
                print("contest has started")
                template_list = [c for c in template_list if c["title"] != contest["title"]]

                sorted_list = [c for c in sorted_list if c["title"] != contest["title"]]
                print("removed",template_list)
                print("removed",sorted_list)
                 
                url = "http://127.0.0.1:8000/message_api/contest_start/"
                response = requests.post(url, json=contests_to_start[0])

                if response.status_code == 200:
                    pass
                else:
                    print(f"⚠️ Failed to send contest '{contest['title']}'. Status: {response.status_code}")

                
                contests_to_start.remove(contest)
        print(contests_to_start)
        await asyncio.sleep(1)  

@api_view(['GET'])
def sorted_consumer(request):
   
    params = pika.URLParameters(os.getenv("rabbit_mq"))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    def callback(ch, method, properties, body):
       
        contest = json.loads(body.decode())  
        if isinstance(contest, list):  
            contest = contest[0]   
        contests_to_start.append(contest)  
        print(f"Contest '{contest['title']}' scheduled for {contest['start_date']} {contest['start_time']}")

    channel.basic_consume(queue='contest_sorted', on_message_callback=callback, auto_ack=True)
    
    print(' [*] sorted Waiting for messages. To exit press CTRL+C')
    
   
    consumer_thread = threading.Thread(target=channel.start_consuming, daemon=True)
    consumer_thread.start()

     
    asyncio.run(check_contests())
    print("Consumer started and checking contests asynchronously")
    return Response({"message": "Consumer started and checking contests asynchronously"})


def convert_dates(obj):
   
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")





@api_view(['GET','POST'])
def temp_publish(request): 
    data = admin_contest_Ser(data=request.data)
    if data.is_valid():
        data = data.validated_data
        for i in template_list:
            
            if i["title"]==data["title"]:
                data["description"] = i["description"]
                data["tags"] = i["tags"]
                data["prize"] = i["prize"]
                break
        else:
                return Response({"error":"Template not found"})
        params = pika.URLParameters(os.getenv("rabbit_mq"))
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        json_data = json.dumps(data, default=convert_dates).encode('utf-8')
        
        channel.basic_publish(exchange='',
                        routing_key='contest_template',
                        body=json_data )
        conn = Contest_serializer(data=data)

        if conn.is_valid():
            conn.save()
            connection.close()
            return Response({"message":"pushed to queue and db"})
            
        else:
            connection.close()
            return Response({"error":conn.errors})
             


    else:
         
        return Response({"error":data.errors})
    
    
   

sorted_list = []

@api_view(['GET'])
def temp_consumer(request):
    params = pika.URLParameters(os.getenv("rabbit_mq"))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    def callback(ch, method, properties, body):
        global sorted_list   
        try:
            data = json.loads(body.decode())   
            if isinstance(data, dict):
                data = [data]  

            if not isinstance(data, list):
                print(" [!] Received non-list data. Skipping...")
                return

            
            sorted_list.extend(data)
            sorted_list.sort(key=lambda x: (x['start_date'], x['start_time']))
            channel.basic_publish(
                exchange='',
                routing_key='contest_sorted',
                body=json.dumps(sorted_list, default=str).encode('utf-8')
            )

            print(f" [x] Processed & Published: {sorted_list}")

        except Exception as e:
            print(f" [!] Error processing message: {e}")

     
    channel.basic_consume(queue='contest_template', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n [!] Stopping consumer...")
        connection.close()
        sys.exit(0)

@api_view(['GET','POST'])
def ack(request):
    
    params = pika.URLParameters(os.getenv("RABBIT_MQ"))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    while True:
        method_frame, header_frame, body = channel.basic_get(queue='testing_streams', auto_ack=False)
        print(method_frame,header_frame,body)
        if method_frame:
            print(f"Acknowledging message: {body.decode()}")
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)  # Acknowledge message
        else:
            print("No more unacknowledged messages.")
            break  # Exit when all messages are acknowledged

    connection.close()


@api_view(['GET','POST','DELETE'])
def contest_template(request):
    if request.method=="GET":
        global template_list
        print(template_list)
        return Response(template_list)

    if request.method=="POST":
        serializer = template_contest_ser(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data 
            temp={}
            temp["title"] = validated_data["title"]
            temp["description"] = validated_data["description"]
            temp["tags"] = validated_data["tags"]
            temp["prize"] = validated_data["prize"]
            template_list.append(serializer.data)
            return Response({"message":"added to template"})
        else:
            return Response({"error":serializer.errors})
    


    if request.method == "DELETE":
        delete_title = request.data.get("title")

        if delete_title not in template_dict.keys():
            return Response({"error": "Template not found"}, status=404)

        del template_dict[delete_title]
        return Response({"message": f"Contest template {delete_title} deleted"})
   