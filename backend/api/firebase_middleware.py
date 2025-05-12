# Note: DRF auth class using firebase for authencitcating a user.

import firebase_admin
from firebase_admin import credentials
import os
from django.conf import settings

class FirebaseAdminInitMiddleware:
    initialized = False

    def __init__(self, get_response):
        self.get_response = get_response
        if not FirebaseAdminInitMiddleware.initialized:
            cred_path = os.path.join(settings.BASE_DIR, "firebase-adminsdk.json")
            cred = credentials.Certificate(cred_path)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            FirebaseAdminInitMiddleware.initialized = True

    def __call__(self, request):
        response = self.get_response(request)
        return response
