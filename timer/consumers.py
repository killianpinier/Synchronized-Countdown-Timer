from .models import Session
from .timer import Response, update_timer

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from datetime import datetime

class TimerConsumer(AsyncWebsocketConsumer):
    # check if session id exists before connecting
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.timer_group_name = f'timer_{self.session_id}'

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
            # Action attribute (in text_data) is useless, but might be usefull in the future
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
    def generate_response(timer):
        return Response(
            timer.id,
            timer.duration.seconds,
            timer.remaining.seconds,
            int(timer.end_at.timestamp() * 1000),
            timer.status,
            datetime.now().timestamp(),
        )
        
    @sync_to_async
    def handle_session(self, data):
        timer = Session.objects.get(session_id=data.get("session_id")).selected_timer

        update_timer(data.get("status"), timer)

        return Response(
            timer.id,
            timer.duration.seconds,
            timer.remaining.seconds,
            int(timer.end_at.timestamp() * 1000),
            timer.status,
            datetime.now().timestamp(),
        )

    async def timer_update(self, event):
        await self.send(text_data=json.dumps(event['timer_data']))