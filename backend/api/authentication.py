# Note: firebase admin is a library in django that allows you to interact with Firebase services.


from firebase_admin import auth as firebase_auth
from rest_framework import authentication, exceptions
from django.contrib.auth.models import User

# Note: you are passing the firebase_admin instance to the authentication class
class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        if not auth_header.startswith('Bearer '):
            raise exceptions.AuthenticationFailed('Invalid token format')

        id_token = auth_header.split('Bearer ')[1]

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
        except Exception as e:
            raise exceptions.AuthenticationFailed('Token not valid')

        uid = decoded_token.get('uid')
        email = decoded_token.get('email')

        try:
            user = User.objects.get(username=uid)
            if user.email != email:
                user.email = email
                user.save()
        except User.DoesNotExist:
            user = User.objects.create(
                username=uid,
                email=email,
            )
        
        user_data = {
            'uid': uid,
            'email': email
        }

        return (user, user_data)