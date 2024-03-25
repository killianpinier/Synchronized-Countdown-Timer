import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Timer
from asgiref.sync import sync_to_async

from .timer import SessionData, Response, update_timer
from datetime import datetime

class TimerConsumer(AsyncWebsocketConsumer):
    # check if session id exists before connecting
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.timer_group_name = f'timer_{self.session_id}'

        #print("Youpi")

        await self.channel_layer.group_add(
            self.timer_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.timer_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            # Action is useless, but might be usefull in the future
            data = json.loads(text_data)
            if data['action'] == 0:
                response = await self.handle_session(data)
                await self.channel_layer.group_send(
                    self.timer_group_name,
                    {
                        'type': 'timer_update',
                        'timer_data': response.to_map()
                    }
                )
            elif data['action'] == 1:
                pass
        except ValueError as e:
                print("Error: ", e)
        except Exception as e:
                print("Error: ", e) 

    @sync_to_async
    def generate_response(timer_id):
        timer = Timer.objects.get(pk=timer_id)
        return Response(
            timer.duration.seconds,
            timer.remaining.seconds,
            int(timer.end_at.timestamp() * 1000),
            timer.status,
            datetime.now().timestamp(),
        )
        
    @sync_to_async
    def handle_session(self, data):
        session_data = SessionData(data.get("timer_id"), data.get("status"))
        timer = Timer.objects.get(pk=session_data.current_timer)
        response = Response(
            timer.duration.seconds,
            timer.remaining.seconds,
            int(timer.end_at.timestamp() * 1000),
            timer.status,
            datetime.now().timestamp(),
        )
        update_timer(session_data.request_status, timer, response)
        timer.save()
        return response

    # async def start_timer(self, user_id, duration):
    #     # Logic to start the timer and update database
    #     timer = Timer.objects.get(user_id=user_id, session_id=self.session_id)
    #     timer.duration = duration
    #     timer.is_running = True
    #     timer.save()

    #     # Send timer update to group
    #     await self.channel_layer.group_send(
    #         self.timer_group_name,
    #         {
    #             'type': 'timer_update',
    #             'timer_data': {'duration': timer.duration, 'is_running': timer.is_running}
    #         }
    #     )

    async def timer_update(self, event):
        await self.send(text_data=json.dumps(event['timer_data']))