# Note: leveraging channels to create a websocket consumer for therapist matching

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TherapistMatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("therapistmatch", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("therapistmatch", self.channel_name)

    async def receive(self, text_data):
        pass

    async def therapistmatch_created(self, event):
        await self.send(text_data=json.dumps(event["data"]))
