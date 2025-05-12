# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.core.asgi import get_asgi_application
# from django.urls import re_path
# from api.consumers import TherapistMatchConsumer

# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#         "websocket": AuthMiddlewareStack(
#             URLRouter(
#                 [
#                     re_path(r"ws/therapistmatch/$", TherapistMatchConsumer.as_asgi()),
#                 ]
#             )
#         ),
#     }
# )

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import re_path
from api.consumers import TherapistMatchConsumer

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    re_path(r"ws/therapistmatch/$", TherapistMatchConsumer.as_asgi()),
                ]
            )
        ),
    }
)