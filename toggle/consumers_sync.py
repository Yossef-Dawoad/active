# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .serializers import ActiveLockObjSerializer


class ActiveLockHandlerConsumer(WebsocketConsumer):

    # groups = ["lockstate_room"] 

    def connect(self):
        self.room_name = 'lockstate_room'
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        message = json.loads(text_data)["message"]
        print(message)
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_channel_name': self.channel_name
            }
        )
      
        # message["user"] = self.scope['user']
        newrecord = ActiveLockObjSerializer(data=message)
        if newrecord.is_valid() and message['validated']:     
            newrecord.save()

    # Receive message from room group
    def chat_message(self, event):
        if self.channel_name != event.get('sender_channel_name'):
            # Send message to WebSocket
            self.send(
                text_data=json.dumps({
                    'message': event['message']
                }))

