from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator




from chat.consumers import ChatConsumer

#Vishnu:
#For web sockets we need to speicy paths like we would for URL pages in HTTP.
#In this case, we want to associate web sockets to run on our username page.
#You see that any web page that has "/messages/username/" it will call the ChatConsumer
#Chat Consumer is managed on Consumers.py I think we only want one consumer, but maybe we can break them out


#AllowedHostsOrignalValidator ensures that only requests from our approved hosts (in this case all domains for now while we test)
#are allowed to interface with our web sockets
#The MiddlewareStack Allows users to maintain continual connection (we want this for sure)


application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    url(r"^messages/(?P<username>[\w.@+-]+)/$", ChatConsumer)
                ]
            )
        )
    )
})