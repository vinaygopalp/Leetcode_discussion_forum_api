from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import Message_serializer,ChatRoom_serializer,User_serializer,Contest_serializer
from chat.models import Message,ChatRoom,User_base as User
from django.shortcuts import redirect
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os 
import sys
import pika

template_dict = {"demo_title": "demo_description"}
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

@api_view(['GET','POST'])
def template_publish(request): 
    data = request.data['message']
    params = pika.URLParameters(os.getenv("rabbit_mq"))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # channel.queue_declare(queue='contest_template')
    channel.basic_publish(exchange='',
                      routing_key='contest_template',
                      body=data)
    print(" [x] Sent {}".format(data))
    connection.close()
    return Response({"message":"RabbitMQ"})

@api_view(['GET'])
def template_consumer(request):
    params = pika.URLParameters(os.getenv("rabbit_mq"))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # channel.queue_declare(queue='contest_template')
    def callback(ch, method, properties, body):
        # if body:
        #     conn = Contest_serializer(data=json.loads(body))
        #     if conn.is_valid():
        #         conn.save()
        #         print(f"pushed")
        #     else:
        #         print(conn.errors)
        print(f" [x] Received {body}")

    channel.basic_consume(queue='contest_template', on_message_callback=callback, auto_ack=False)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
     
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n [!] Stopping consumer...")
        connection.close()   
        sys.exit(0)   
 







@api_view(['GET','POST'])
def sorted_publish(request): 
    data = request.data
    data = json.dumps(data)
    params = pika.URLParameters(os.getenv("rabbit_mq"))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # channel.queue_declare(queue='contest_template')
    channel.basic_publish(exchange='',
                      routing_key='testing_streams',
                      body=data)
    print(" [x] Sent {}".format(data))
    connection.close()
    return Response({"message":"RabbitMQ"})

@api_view(['GET'])
def sorted_consumer(request):
    params = pika.URLParameters(os.getenv("rabbit_mq"))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # channel.queue_declare(queue='contest_template')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        body = json.loads(body)
        body["description"] = template_dict[body["title"]]
        
        print(body)
        conn = Contest_serializer(data=body)
        if conn.is_valid():
            conn.save()
            print(f"pushed")
        else:
            print(conn.errors)
        

    channel.basic_consume(queue='testing_streams', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
     
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
        global template_dict
        return Response({"contest_template":json.dumps(template_dict)})

    if request.method=="POST":
        template_dict = request.data
        template_dict['title'] = request.data.get("description")
        return Response({"message":"contest_template added"})


    if request.method == "DELETE":
        delete_title = request.data.get("title")

        if delete_title not in template_dict.keys():
            return Response({"error": "Template not found"}, status=404)

        del template_dict[delete_title]
        return Response({"message": f"Contest template {delete_title} deleted"})
   