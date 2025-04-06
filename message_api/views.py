from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import Message_serializer,ChatRoom_serializer,User_serializer
from chat.models import Message,ChatRoom,ScheduledContest
from django.shortcuts import redirect
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os 
import sys
import pika
from datetime import date, time, datetime
 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import redis
 
import time

from datetime import datetime
from dateutil import parser
 
 
# template_list = []
# sorted_list = []
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

 

# actual_start={}
# @api_view(['POST','GET'])
# def contest_start(request):
    
#     if request.method == "POST" :
#         global actual_start
#         actual_start = {}
#         actual_start = request.data
#         print(actual_start)

#         data = request.data
#         return Response(data)
#     if request.method == "GET":
#         return Response(actual_start) 


 
# contests_to_start = []

# async def check_contests():
#     global template_list
#     global sorted_list
#     """Background task to check if any contest should start."""
#     while True:
#         current_date = datetime.now().date()
#         current_time = datetime.now().time().replace(microsecond=0)
#         print(f"Checking contests at {current_date} {current_time}")
        
#         for contest in contests_to_start[:]: 
#             if isinstance(contest, list):  
#                 contest = contest[0]   
#             start_date = contest["start_date"]
#             start_time = contest["start_time"]
#             print(start_date,start_time)
#             if start_date <= str(current_date) and start_time <= str(current_time):
#                 print("contest has started")
#                 template_list = [c for c in template_list if c["title"] != contest["title"]]

#                 sorted_list = [c for c in sorted_list if c["title"] != contest["title"]]

#                 url = os.getenv("constest_start_url")
#                 response = requests.post(url, json=contests_to_start[0])

#                 if response.status_code == 200:
#                     pass
#                 else:
#                     print(f"Failed to send contest '{contest['title']}'. Status: {response.status_code}")

                
#                 contests_to_start.remove(contest)
#         print(contests_to_start)
#         await asyncio.sleep(250)  

# @api_view(['GET'])
# def sorted_consumer(request):
   
#     params = pika.URLParameters(os.getenv("rabbit_mq"))
#     connection = pika.BlockingConnection(params)
#     channel = connection.channel()

#     def callback(ch, method, properties, body):
       
#         contest = json.loads(body.decode())  
#         if isinstance(contest, list):  
#             contest = contest[0]   
#         contests_to_start.append(contest)  
#         print(f"Contest '{contest['title']}' scheduled for {contest['start_date']} {contest['start_time']}")

#     channel.basic_consume(queue='contest_sorted', on_message_callback=callback, auto_ack=True)
    
#     print(' [*] sorted Waiting for messages. To exit press CTRL+C')
    
   
#     consumer_thread = threading.Thread(target=channel.start_consuming, daemon=True)
#     consumer_thread.start()

     
#     asyncio.run(check_contests())
#     print("Consumer started and checking contests asynchronously")
#     return Response({"message": "Consumer started and checking contests asynchronously"})


def convert_dates(obj):
   
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")





# @api_view(['GET','POST'])
# def temp_publish(request): 
#     data = admin_contest_Ser(data=request.data)
#     print("DEBUG available templates (raw):", r.hkeys("contest_templates"))
#     print("DEBUG available templates (decoded):", [key.decode('utf-8') for key in r.hkeys("contest_templates")])
#     print("DEBUG searching for template_id:", template_id)

#     if data.is_valid():
#         data = data.validated_data
#         for i in template_list:
            
#             if i["title"]==data["title"]:
#                 data["description"] = i["description"]
#                 data["tags"] = i["tags"]
#                 data["prize"] = i["prize"]
#                 break
#         else:
#                 return Response({"error":"Template not found"})
#         params = pika.URLParameters(os.getenv("rabbit_mq"))
#         connection = pika.BlockingConnection(params)
#         channel = connection.channel()
#         json_data = json.dumps(data, default=convert_dates).encode('utf-8')
        
#         channel.basic_publish(exchange='',
#                         routing_key='contest_template',
#                         body=json_data )
#         conn = Contest_serializer(data=data)

#         if conn.is_valid():
#             conn.save()
#             connection.close()
#             return Response({"message":"pushed to queue and db"})
            
#         else:
#             connection.close()
#             return Response({"error":conn.errors})
             


#     else:
         
#         return Response({"error":data.errors})
    
    
   

# sorted_list = []

# @api_view(['GET'])
# def temp_consumer(request):
#     params = pika.URLParameters(os.getenv("rabbit_mq"))
#     connection = pika.BlockingConnection(params)
#     channel = connection.channel()

#     def callback(ch, method, properties, body):
#         global sorted_list   
#         try:
#             data = json.loads(body.decode())   
#             if isinstance(data, dict):
#                 data = [data]  

#             if not isinstance(data, list):
#                 print(" [!] Received non-list data. Skipping...")
#                 return

            
#             sorted_list.extend(data)
#             sorted_list.sort(key=lambda x: (x['start_date'], x['start_time']))
#             channel.basic_publish(
#                 exchange='',
#                 routing_key='contest_sorted',
#                 body=json.dumps(sorted_list, default=str).encode('utf-8')
#             )

#             print(f" [x] Processed & Published: {sorted_list}")

#         except Exception as e:
#             print(f" [!] Error processing message: {e}")

     
#     channel.basic_consume(queue='contest_template', on_message_callback=callback, auto_ack=True)

#     print(' [*] Waiting for messages. To exit press CTRL+C')

#     try:
#         channel.start_consuming()
#     except KeyboardInterrupt:
#         print("\n [!] Stopping consumer...")
#         connection.close()
#         sys.exit(0)

# @api_view(['GET','POST'])
# def ack(request):
    
#     params = pika.URLParameters(os.getenv("RABBIT_MQ"))
#     connection = pika.BlockingConnection(params)
#     channel = connection.channel()

#     while True:
#         method_frame, header_frame, body = channel.basic_get(queue='testing_streams', auto_ack=False)
#         print(method_frame,header_frame,body)
#         if method_frame:
#             print(f"Acknowledging message: {body.decode()}")
#             channel.basic_ack(delivery_tag=method_frame.delivery_tag)  # Acknowledge message
#         else:
#             print("No more unacknowledged messages.")
#             break  # Exit when all messages are acknowledged

#     connection.close()
    
  
r = redis.Redis(
      host=os.getenv("contest_host"),
    port=os.getenv("contest_port"),
    decode_responses=True,
    username=os.getenv("contest_username"),
    password=os.getenv("contest_password"),
)
 
TEMPLATE_KEY = os.getenv("contest_template_key")
SCHEDULE_KEY = os.getenv("contest_schedule_key")
# --- Helper Functions ---
def create_template(template_id, title, description, tags, prize):
    template_data = {
        "title": title,
        "description": description,
        "tags": tags,
        "prize": prize
    }
    r.hset(TEMPLATE_KEY, template_id, json.dumps(template_data))


def schedule_contest(contest_id, template_id, start_datetime, end_datetime, problems_id):
    start_dt = parser.parse(start_datetime)
    end_dt = parser.parse(end_datetime)

    contest_data = {
        "contest_id": contest_id,
        "template_id": template_id,
        "start_datetime": start_dt.isoformat(),
        "end_datetime": end_dt.isoformat(),
        "problems_id": json.dumps(problems_id)
    }

    r.hset(f"contest:{contest_id}", mapping=contest_data)
    r.zadd(SCHEDULE_KEY, {contest_id: start_dt.timestamp()})
    ScheduledContest.objects.create(
        contest_id=contest_id,
        template_id=template_id,
        start_datetime=start_dt,
        end_datetime=end_dt,
        problems_id=problems_id  # in DB, problems_id will be actual Python list
    )
    print(f"Contest {contest_id} scheduled successfully at timestamp {start_dt.timestamp()}!")

 
@csrf_exempt
def contest_template(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title", "").strip()
            description = data.get("description", "").strip()
            tags = data.get("tags", [])
            prize = data.get("prize", "")

            if not title or not description:
                return JsonResponse({"error": "Title and description are required."}, status=400)

            create_template(title, title, description, tags, prize)

            return JsonResponse({"message": "Template created successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
def schedule_contest_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            start_date = data.get("start_date")
            start_time = data.get("start_time")
            end_date = data.get("end_date")
            end_time = data.get("end_time")
            problems_id = data.get("problems_id", [])
            contest_id = data.get("title", "").strip()
            template_id = data.get("title", "").strip()

            if not (start_date and start_time and end_date and end_time):
                return JsonResponse({"error": "All date and time fields are required."}, status=400)

            start_datetime = f"{start_date} {start_time}"
            end_datetime = f"{end_date} {end_time}"

            schedule_contest(contest_id, template_id, start_datetime, end_datetime, problems_id)

            return JsonResponse({"message": "Contest scheduled successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)

from datetime import datetime
from datetime import datetime

from datetime import datetime

 
@csrf_exempt
def contest_start(request):
    if request.method == "GET":
        try:
            current_timestamp = int(time.time())  
            print(f"Current UTC time: {current_timestamp}")

            ready_contests = r.zrangebyscore(SCHEDULE_KEY, 0, current_timestamp)
            print(f"Contest IDs ready to start: {ready_contests}")

            if ready_contests:
                contests_data = []
                for contest_id in ready_contests:
                    contest_id = str(contest_id)  
                    contest_key = f"contest:{contest_id}"
                    contest_data = r.hgetall(contest_key)

                    if contest_data:
                      
                        contest_data = {k.decode('utf-8') if isinstance(k, bytes) else k: 
                                        v.decode('utf-8') if isinstance(v, bytes) else v 
                                        for k, v in contest_data.items()}

                        print(f"Contest {contest_id} data: {contest_data}")  

                        problems_id_raw = contest_data.get("problems_id")
                        if problems_id_raw:
                            try:
                                contest_data["problems_id"] = json.loads(problems_id_raw)
                            except json.JSONDecodeError:
                                contest_data["problems_id"] = []
                        else:
                            contest_data["problems_id"] = []

                      
                        end_datetime_str = contest_data.get("end_datetime")

                        print(f"Contest {contest_id} end_datetime: {end_datetime_str}")   

                         
                        end_timestamp = 0

                        if end_datetime_str:
                           
                            end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%dT%H:%M:%S")
                            
                            
                            end_timestamp = int(end_datetime.timestamp())
                            print(f"Contest {contest_id} end timestamp: {end_timestamp}")

                        
                        print(f"Comparing current time {current_timestamp} with contest end timestamp {end_timestamp}")
                        if current_timestamp >= end_timestamp:
                          
                            r.delete(contest_key)   
                            r.zrem(SCHEDULE_KEY, contest_id)   
                            print(f"Contest {contest_id} deleted")
                            template_id = contest_data.get("template_id")
                            if template_id:
                                r.hdel(TEMPLATE_KEY, template_id)  

                        contests_data.append(contest_data)

                return JsonResponse({"contests": contests_data})
            else:
                return JsonResponse({"message": "No contests ready to start yet."})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def list_templates(request):
    if request.method == "GET":
        try:
            templates = r.hgetall(TEMPLATE_KEY)
            templates = {k: json.loads(v) for k, v in templates.items()}
            return JsonResponse({"templates": templates})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
def delete_all_contests(request):
    if request.method == "POST":
        try:
            scheduled_contests = r.zrange(SCHEDULE_KEY, 0, -1)
            for contest_id in scheduled_contests:
                r.delete(f"contest:{contest_id}")

            r.delete(SCHEDULE_KEY)

            return JsonResponse({"message": "All contests deleted successfully."})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
def delete_all_templates(request):
    if request.method == "POST":
        try:
            r.delete(TEMPLATE_KEY)
            return JsonResponse({"message": "All templates deleted successfully."})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
@csrf_exempt
def view_all_scheduled_contests(request):
    if request.method == "GET":
        try:
          
            scheduled_contests = r.zrange(SCHEDULE_KEY, 0, -1)  
            print(f"Scheduled Contest IDs: {scheduled_contests}")  

            contests_data = []
            for contest_id in scheduled_contests:
                contest_key = f"contest:{contest_id}"
                contest_data = r.hgetall(contest_key)
                print(f"Contest {contest_id} data: {contest_data}") 
                if contest_data:
                    contests_data.append(contest_data)

            if contests_data:
                return JsonResponse({"scheduled_contests": contests_data})
            else:
                return JsonResponse({"message": "No contests are scheduled yet."})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)
