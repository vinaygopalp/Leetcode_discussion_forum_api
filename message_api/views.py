from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import Message_serializer,ChatRoom_serializer,User_serializer
from chat.models import Message,ChatRoom, ScheduledContest,Users,Problem
from django.shortcuts import redirect
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os 
from datetime import date, time, datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import redis
import time
from datetime import datetime
from dateutil import parser
from zoneinfo import ZoneInfo  # Built-in in Python 3.9+
INDIA_TZ = ZoneInfo("Asia/Kolkata")

r = redis.Redis(
      host=os.getenv("contest_host"),
    port=os.getenv("contest_port"),
    decode_responses=True,
    username=os.getenv("contest_username"),
    password=os.getenv("contest_password"),
)
 
TEMPLATE_KEY = os.getenv("contest_template_key")
SCHEDULE_KEY = os.getenv("contest_schedule_key")
 
@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
def get_message(request, room_name=None):
    if request.method == "GET":
        if room_name:
            try:
                rooms = ChatRoom.objects.get(room=room_name)
            except ChatRoom.DoesNotExist:
                return Response({"error": "Room not found"}, status=404)
            messages = Message.objects.filter(room=rooms).order_by('timestamp')
            
        else:
            messages = Message.objects.all().order_by('timestamp')
        serializer = Message_serializer(messages, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = Message_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors": serializer.errors})
    elif request.method == "DELETE":
        message = Message.objects.get(id=request.data["id"])
        message.delete()
        return Response({"message": "Message Deleted"})
    
@csrf_exempt
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

@csrf_exempt
@api_view(['GET','POST','DELETE'])
def add_user(request):
    if request.method == "GET":
        users = Users.objects.all()
        serializer = User_serializer(users, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = User_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors":serializer.errors})
    elif request.method == "DELETE":
        user = Users.objects.get(id=request.data["id"])
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

 


def convert_dates(obj):
   
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def create_template(template_id, title, description, tags, prize):
    template_data = {
        "title": title,
        "description": description,
        "tags": tags,
        "prize": prize
    }
    r.hset(TEMPLATE_KEY, template_id, json.dumps(template_data))

@csrf_exempt
def schedule_contest(contest_id, template_id, start_datetime, end_datetime, problems_id):
    # Parse and convert to IST
    start_dt = parser.parse(start_datetime)
    end_dt = parser.parse(end_datetime)

    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    else:
        start_dt = start_dt.astimezone(ZoneInfo("Asia/Kolkata"))

    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    else:
        end_dt = end_dt.astimezone(ZoneInfo("Asia/Kolkata"))

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
        problems_id=problems_id
    )

    print(f"[SCHEDULED] Contest: {contest_id} | Start (IST): {start_dt} | End (IST): {end_dt}")

 
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

            problems_id_int = [int(pid) for pid in problems_id]
            existing_ids = set(Problem.objects.filter(id__in=problems_id_int).values_list('id', flat=True))
            invalid_ids = [pid for pid in problems_id_int if pid not in existing_ids]

            if invalid_ids:
                return JsonResponse({
                    "error": f"The following problem_id(s) do not exist: {invalid_ids}"
                }, status=400)

            start_datetime = f"{start_date} {start_time}"
            end_datetime = f"{end_date} {end_time}"

            print(f"[RECEIVED] IST datetime strings -> Start: {start_datetime}, End: {end_datetime}")

            schedule_contest(contest_id, template_id, start_datetime, end_datetime, problems_id_int)

            return JsonResponse({"message": "Contest scheduled successfully"})

        except Exception as e:
            print(f"[ERROR] while scheduling: {str(e)}")
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def contest_start(request):
    if request.method == "GET":
        try:
            current_timestamp = int(time.time())  
            
            scheduled_contests = r.zrange(SCHEDULE_KEY, 0, -1)  
            
            contests_data = []
            for contest_id in scheduled_contests:
                contest_key = f"contest:{contest_id}"
                contest_data = r.hgetall(contest_key)
                if contest_data:
                    # Decode bytes to strings
                    contest_data = {
                        k.decode('utf-8') if isinstance(k, bytes) else k: 
                        v.decode('utf-8') if isinstance(v, bytes) else v 
                        for k, v in contest_data.items()
                    }

                    start_datetime_str = contest_data.get("start_datetime")
                    end_datetime_str = contest_data.get("end_datetime")
                    problems_id_raw = contest_data.get("problems_id")

                    # Parse timestamps
                    start_ts = int(datetime.fromisoformat(start_datetime_str).astimezone(INDIA_TZ).timestamp())
                    end_ts = int(datetime.fromisoformat(end_datetime_str).astimezone(INDIA_TZ).timestamp()) if end_datetime_str else 0

                    # If contest ended, delete it
                    if current_timestamp >= end_ts:
                        r.delete(contest_key)
                        r.zrem(SCHEDULE_KEY, contest_id)
                        print(f"Contest {contest_id} deleted")
                        template_id = contest_data.get("template_id")
                        if template_id:
                            r.hdel(TEMPLATE_KEY, template_id)
                        continue  # Don't include in response

                    # Determine if contest has started
                    if current_timestamp >= start_ts:
                        if problems_id_raw:
                            try:
                                contest_data["problems_id"] = json.loads(problems_id_raw)
                            except json.JSONDecodeError:
                                contest_data["problems_id"] = []
                        else:
                            contest_data["problems_id"] = []
                    else:
                        contest_data["problems_id"] = []

                    contests_data.append(contest_data)

            return JsonResponse({"contests": contests_data})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

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

@csrf_exempt
def test(request):
    return JsonResponse({"message":"success"})