import asyncio
import json

from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from .models import Thread, ChatMessage


#Consumers are what let our web sockets communicate with channels.
#They are most of the back end routing of a client side request being managed by our server.

#the await in front of functions is part of the async functinality
#a function can be called, but it will then wait for everything else downstream to finish and return an answer
class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self,event):
        print("connected", event)

        #The other user is the person we are chatting with
        #it is pulled out by looking at the URL of the page.
        #The username is the flag of the other username, it is coming through the routing.py file of ?P<username>
        other_user = self.scope['url_route']['kwargs']['username']
        
        
        #Similar to above, pulling out the user of the session gets who I am
        me = self.scope['user']
        #print(other_user,me)

        #This function goes out to find the thread object given who i am and who the other user is
        #The thread object will help understand what is our unique chat room ID
        thread_obj = await self.get_thread(me,other_user)
        print(me, thread_obj.id)


        #I'm assinging the thread object to the class here since it'll be referenced later

        self.thread_obj = thread_obj
        
        #chat room is the thread object ID, assigning it to a variable here!
        chat_room = f"thread_{thread_obj.id}"
        #also storing it in the class
        self.chat_room = chat_room

        #Now for Django Channels!
        #I'm adding a group layer to the django channel.
        #The first value of chat_room is our chat room id
        #The channel name
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )



        await self.send({
            "type": "websocket.accept"
        })

    
    async def websocket_receive(self,event):
        print("recieve", event)
        #Grabbing the text field of a message
        front_text = event.get('text',None)

        #In the event it is not None (there is a message to relay)
        if front_text is not None:
            #load the json dict
            loaded_dict_data = json.loads(front_text)
            
            #parse the message out with the message key
            msg = loaded_dict_data.get('message')
            print(msg)

            #as above, grabbing the user
            user = self.scope['user']
            username = 'default'

            #If the user is logged in - update with proper username
            if user.is_authenticated:
                username = user.username

            #The response is a dictionary of the message and user who sent it
            myResponse = {
                'message': msg,
                'username': username
            }

            #sending the chat message to the database
            await self.create_chat_message(msg)

            #broadcasts the message event to be sent
            #in the django channel does a group send
            #to the channel
            await self.channel_layer.group_send(
                self.chat_room,
                {
                    "type": "chat_message",
                    "text": json.dumps(myResponse)
                }
            )
    

    async def chat_message(self,event):
        #sends the actual message
        #when an object is of "chat_message"
        #it will send a socket of the json object
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })
    
    async def websocket_disconnect(self,event):
        print("disconnected", event)
    

    #THIS DECORATOR IS CRITICAL TO PREVENT MEMORY LEAKS/OVERLOADING YOUR DATABASE
    #If you do not have this - it may result in too many connections to your database
    @database_sync_to_async
    def get_thread(self,user,other_username):
        return Thread.objects.get_or_new(user,other_username)[0]
    
    @database_sync_to_async
    def create_chat_message(self, msg):
        thread_obj = self.thread_obj
        me         = self.scope['user']
        return ChatMessage.objects.create(thread=thread_obj, user=me, message=msg)