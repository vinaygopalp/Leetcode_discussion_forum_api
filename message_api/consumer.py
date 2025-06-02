import json
import redis
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from chat.models import Contest_Particpants, Contest_Leaderboard, ScheduledContest, Users

from .serializer import ContestParticipantSerializer
from .views import reward_pointss, sanitize_group_name, rank_users_by_entry_time
#from .redis_config import redis_client
#from .rabbitmq_config import channel  # assuming you import RabbitMQ connection/channel here
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
 
import pika
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
 
class ContestConsumer:
    def __init__(self):
        self.channel = channel

    def start(self):
        self.channel.basic_consume(
            queue='contest_user_submissions',
            on_message_callback=self.consumer_callback
        )
        print("[*] Waiting for messages in contest_user_submissions. To exit press CTRL+C")
        self.channel.start_consuming()

    def consumer_callback(self, ch, method, properties, body):
        try:
            data = json.loads(body)
            print(f"[*] Received message: {data}")

            user_id = str(data["user_id"])
            total_test_case = data["total_tests"]
            test_cases_passed = data["test_cases_passed"]
            status = data["status"]
            problem_id = data["problem_id"]

            contest_par = Contest_Particpants.objects.filter(user=user_id, active=True).select_related('contest').first()
            print(f"[*] Contest Participant: {contest_par}")

            if contest_par:
                serializer_contest = ContestParticipantSerializer(contest_par)
                serialized_data = serializer_contest.data
                contest_id = contest_par.contest.id
                contest_title = serialized_data['contest']['contest_id']
                contest_start_ts = serialized_data['contest']['start_datetime']
                contest_end_ts = serialized_data['contest']['end_datetime']

                if problem_id in serialized_data['contest']['problems_id']:
                    new_points = int(reward_pointss(contest_start_ts, contest_end_ts, total_test_case, test_cases_passed))

                    redis_key = f"leaderboard:{contest_par.contest.id}"
                    leaderboard_entry = Contest_Leaderboard.objects.filter(contest_participant=contest_par).first()

                    if not leaderboard_entry:
                        leaderboard_entry = Contest_Leaderboard.objects.create(
                            contest_participant=contest_par,
                            total_solved_problem=[problem_id],
                            reward_points=new_points
                        )
                    else:
                        solved_problems = leaderboard_entry.total_solved_problem or []
                        existing_points = leaderboard_entry.reward_points or 0

                        if problem_id not in solved_problems:
                            solved_problems.append(problem_id)
                            leaderboard_entry.total_solved_problem = solved_problems
                            leaderboard_entry.reward_points = existing_points + new_points
                            leaderboard_entry.save()
                        elif new_points > existing_points:
                            leaderboard_entry.reward_points = new_points
                            leaderboard_entry.save()

                    redis_client.zadd(redis_key, {user_id: leaderboard_entry.reward_points})
                    print(f"[*] User {user_id} scored {leaderboard_entry.reward_points} points for problem {problem_id} in contest {contest_title}")

                    channel_layer = get_channel_layer()
                    group_name = f"leaderboard_{sanitize_group_name(str(contest_title))}"
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "leaderboard_message",
                            "message": self.backend_leaderboard(contest_id)
                        }
                    )

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"[!] Error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def backend_leaderboard(self, contest_id):
        redis_key = f"leaderboard:{contest_id}"
        leaderboard_data = redis_client.zrevrange(redis_key, 0, -1, withscores=True)

        if not leaderboard_data:
            return []

        user_ids = [int(uid) for uid, _ in leaderboard_data]
        users = Users.objects.filter(id__in=user_ids)
        user_map = {user.id: user.username for user in users}

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
