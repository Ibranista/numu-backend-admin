from django.shortcuts import render
from .firebase_utils import firebase_admin

from django.contrib.auth.models import User
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import FirebaseUserSerializer, NoteSerializer, ChildSerializer, ExpertiseSerializer, TherapistSerializer, TherapistMatchSerializer
from .child_serializers.children_serializers  import LanguageSerializer,ChildConcernSerializer
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
# from rest_framework.serializers import ModelSerializer
from .models import Note,Child,UserProfile,Expertise,Therapist, TherapistMatch
from .models import Language,Concern
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import TherapistMatchNestedSerializer
from .pagination import CustomPagination

# user details view
class UserDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        firebase_uid = kwargs.get('firebase_uid')
        # print(f"Requested user details for firebase_uid: {firebase_uid}")
        # own profile
        if str(request.user.username) != firebase_uid:
            # print(f"Unauthorized access attempt by {request.user.username} for profile {firebase_uid}")
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            user_profile = UserProfile.objects.get(firebase_uid=firebase_uid)
            user = user_profile.user
            user_data = {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'firebase_uid': firebase_uid,
                'role': user_profile.role,
            }
            # print(f"Returning user details: {user_data}")
            return Response(user_data)
        except UserProfile.DoesNotExist:
            # print(f"UserProfile not found for firebase_uid: {firebase_uid}")
            return Response({'detail': 'User not found'}, status=404)

class CreateUserView(generics.CreateAPIView):
    serializer_class = FirebaseUserSerializer
    permission_classes = [AllowAny]
    authentication_classes = [] 

    def post(self, request):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'A user with this email already exists.'}, status=400)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.save()
            return Response(user_data, status=201)
        return