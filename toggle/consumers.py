# chat/consumers.py
import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer 
from .serializers import ActiveLockObjSerializer


class ActiveLockHandlerConsumer(AsyncWebsocketConsumer):
    # groups = ["lockstate_room"] 

    async def connect(self):
        self.room_name = 'lockstate_room'
        # Join room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        message = json.loads(text_data)["message"]
        # save event to db
        await self.save_Event_db(message)
        # Send message to room group
        await self.channel_layer.group_send( self.room_name,
            {   'type': 'event_message',
                'message': message,
                'sender_channel_name': self.channel_name }
        )


    # Receive message from room group
    async def event_message(self, event):
        if self.channel_name != event.get('sender_channel_name'):
            # Send message to WebSocket
            await self.send(
                text_data=json.dumps({
                    'message': event['message']
                }))

    @sync_to_async
    def save_Event_db(self, event):     
        # message["user"] = self.scope['user']
        newrecord = ActiveLockObjSerializer(data=event)
        if newrecord.is_valid() and event['validated']:     
            newrecord.save()


