from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import *
from chat.models import Message,ChatRoom, ScheduledContest,Users,Problem, Contest_Particpants, Contest_Leaderboard
from django.shortcuts import redirect
import json
from openai import OpenAI
from dotenv import load_dotenv
import os 
from datetime import date, time, datetime, timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import redis
from dateutil import parser
from zoneinfo import ZoneInfo  # Built-in in Python 3.9+
import pika
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

INDIA_TZ = ZoneInfo("Asia/Kolkata")
load_dotenv()

r = redis.Redis(
      host=os.getenv("contest_host"),
    port=os.getenv("contest_port"),
    decode_responses=True,
    username=os.getenv("contest_username"),
    password=os.getenv("contest_password"),
)
 
params = pika.URLParameters(os.getenv("RABBITMQ_URL"))
connection = pika.BlockingConnection(params)
channel = connection.channel()

redis_client = redis.Redis(
    host= os.getenv("leaderboard_queue_host"),  
    port=os.getenv("leaderboard_queue_port"),
    decode_responses=True,
    username=os.getenv("contest_username"),
    password= os.getenv("leaderboard_queue_password") # optional: gets strings instead of bytes
)

channel.queue_declare(queue='contest_user_submissions', durable=True)
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

@csrf_exempt
def convert_dates(obj):
   
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

@csrf_exempt
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
                                redis_key = f"leaderboard:{contest_id}"
                                
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

def parse_iso_datetime(dt_str):
    """Parses ISO datetime string (e.g., '2025-05-23T09:23:14Z') into a timezone-aware datetime object."""
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(timezone.utc)

def reward_pointss(contest_start_ts, contest_end_ts, entered_ts, total_test_case, test_cases_passed):
    contest_start = parse_iso_datetime(contest_start_ts)
    contest_end = parse_iso_datetime(contest_end_ts)
    entered = parse_iso_datetime(entered_ts)

    if entered < contest_start or entered > contest_end:
        return 0

    base_points = 100
    points_per_test_case = 100
    accuracy_ratio = test_cases_passed / total_test_case if total_test_case else 0
    earned_points =  int(points_per_test_case * accuracy_ratio )

    return earned_points

def rank_users_by_entry_time(users_data):
    valid_entries = []
    for user in users_data:
        contest_start = parse_iso_datetime(user['contest_start_ts'])
        entered = parse_iso_datetime(user['entered_ts'])
        time_diff = (entered - contest_start).total_seconds()
        if time_diff >= 0:
            valid_entries.append((user['user_id'], time_diff))
    valid_entries.sort(key=lambda x: x[1])
    return [user_id for user_id, _ in valid_entries]
import re

def sanitize_group_name(name: str) -> str:
    # Replace invalid characters with underscores
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name)[:90] 

@csrf_exempt
def consumer(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"[DATA] {data}")
        user_id = str(data["user_id"])
        total_test_case = data["total_tests"]
        test_cases_passed = data["test_cases_passed"]
        status = data["status"]
        problem_id = data["problem_id"]

        contest_par = Contest_Particpants.objects.filter(user=user_id, active=True).select_related('contest').first()

        if contest_par:
            serializer_contest = ContestParticipantSerializer(contest_par)
            serialized_data = serializer_contest.data
            print("serialized_data",serialized_data)
            contest_id = contest_par.contest.id
            contest_start_ts = serialized_data['contest']['start_datetime']
            contest_end_ts = serialized_data['contest']['end_datetime']
            entered_ts = serialized_data['entered_time']

            if problem_id  in serialized_data['contest']['problems_id']:
                reward_point = reward_pointss(
                    contest_start_ts, contest_end_ts, entered_ts,
                    total_test_case, test_cases_passed
                )
                print(f"[✓] Reward points for user {user_id}: {reward_point}")
                reward_points = int(reward_point)
                redis_key = f"leaderboard:{contest_par.contest.id}"
                leaderboard_entry = Contest_Leaderboard.objects.filter(contest_participant=contest_par).first()
                if not leaderboard_entry:
                    leaderboard_entry = Contest_Leaderboard.objects.create(
                        contest_participant=contest_par,
                        total_solved_problem=[],
                        reward_points=reward_points
                    )
                    leaderboard_entry.save()
                else:
                        solved_problems = leaderboard_entry.total_solved_problem or []
                        if problem_id not in solved_problems:
                            solved_problems.append(problem_id)
                            reward_points = leaderboard_entry.reward_points or 0
                            reward_points += reward_point
                            leaderboard_entry.total_solved_problem = solved_problems
                            leaderboard_entry.save()

                redis_client.zadd(redis_key,{user_id: reward_points})
                channel_layer = get_channel_layer()
                group_name = f"leaderboard_{sanitize_group_name(str(contest_id))}"
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "leaderboard_message",
                        "message": backend_leaderboard(contest_id)
                    }
                )

                print(f"[✓] Leaderboard updated for user {user_id} in contest {contest_par.contest.id}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[!] Error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

@csrf_exempt
def get_leaderboard(request):
    contest_id = request.GET.get("contest_id")
    redis_key = f"leaderboard:{contest_id}"
    leaderboard_data = redis_client.zrevrange(redis_key, 0, -1, withscores=True)

    if not leaderboard_data:
        return []

    user_ids = [int(uid) for uid, _ in leaderboard_data]
    users = Users.objects.filter(id__in=user_ids)
    user_map = {user.id: user.username for user in users}

    # Group users by score
    score_groups = {}
    for uid, score in leaderboard_data:
        uid = int(uid)
        score = int(score)
        score_groups.setdefault(score, []).append(uid)

    final_leaderboard = []

    for score in sorted(score_groups.keys(), reverse=True):
        tied_users = score_groups[score]
        
        if len(tied_users) == 1:
            uid = tied_users[0]
            final_leaderboard.append({
                "user_id": uid,
                "user_name": user_map.get(uid, "Unknown"),
                "score": score
            })
        else:
            participants = Contest_Particpants.objects.filter(
                user_id__in=tied_users,
                contest_id=contest_id
            ).select_related('contest')

            user_entry_data = []
            for part in participants:
                user_entry_data.append({
                    "user_id": part.user_id,
                    "entered_ts": part.entered_time.isoformat(),
                    "contest_start_ts": part.contest.start_datetime.isoformat()
                })

            sorted_user_ids = rank_users_by_entry_time(user_entry_data)
            for uid in sorted_user_ids:
                final_leaderboard.append({
                    "user_id": uid,
                    "user_name": user_map.get(uid, "Unknown"),
                    "score": score
                })
    #final_leaderboard = json.dumps(final_leaderboard, default=convert_dates)
    return JsonResponse({"message":final_leaderboard})

def backend_leaderboard(contest_id):
    #contest_id = request.GET.get("contest_id")
    redis_key = f"leaderboard:{contest_id}"
    leaderboard_data = redis_client.zrevrange(redis_key, 0, -1, withscores=True)

    if not leaderboard_data:
        return []

    user_ids = [int(uid) for uid, _ in leaderboard_data]
    users = Users.objects.filter(id__in=user_ids)
    user_map = {user.id: user.username for user in users}

    # Group users by score
    score_groups = {}
    for uid, score in leaderboard_data:
        uid = int(uid)
        score = int(score)
        score_groups.setdefault(score, []).append(uid)

    final_leaderboard = []

    for score in sorted(score_groups.keys(), reverse=True):
        tied_users = score_groups[score]
        
        if len(tied_users) == 1:
            uid = tied_users[0]
            final_leaderboard.append({
                "user_id": uid,
                "user_name": user_map.get(uid, "Unknown"),
                "score": score
            })
        else:
            participants = Contest_Particpants.objects.filter(
                user_id__in=tied_users,
                contest_id=contest_id
            ).select_related('contest')

            user_entry_data = []
            for part in participants:
                user_entry_data.append({
                    "user_id": part.user_id,
                    "entered_ts": part.entered_time.isoformat(),
                    "contest_start_ts": part.contest.start_datetime.isoformat()
                })

            sorted_user_ids = rank_users_by_entry_time(user_entry_data)
            for uid in sorted_user_ids:
                final_leaderboard.append({
                    "user_id": uid,
                    "user_name": user_map.get(uid, "Unknown"),
                    "score": score
                })
    return final_leaderboard


@csrf_exempt
def start_consuming(request):
    if request.method == "GET":
        channel.basic_consume(queue='contest_user_submissions', on_message_callback=consumer)

        print('[*] Waiting for messages in contest_user_submissions. To exit press CTRL+C')
        channel.start_consuming()

        return JsonResponse({"message":"success"})

 
@csrf_exempt
def contest_registration(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            contest_id = data.get("contest_id")

            if not user_id or not contest_id:
                return JsonResponse({"error": "User ID and Contest ID are required."}, status=400)

            registration = Contest_Particpants.objects.filter(user_id=user_id, contest_id=contest_id).first()
            if not registration:
                registration = Contest_Particpants.objects.create(user_id=user_id, contest_id=contest_id, active=True)

            return JsonResponse({
                "message": "User registered successfully.",
                "registration": registration.id
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)