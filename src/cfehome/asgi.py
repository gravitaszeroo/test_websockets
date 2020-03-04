import os
import djangofrom channels.routing import get_default_application

#Vishnu
#This is boiler plate ASGI code to get us set up when we go to production.
#shouldn't need to edit this beyond swapping out cfehome for our project name
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cfehome.settings")
django.setup()
application = get_default_application()