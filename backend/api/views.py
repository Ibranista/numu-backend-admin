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
    
class ChildListCreate(generics.ListCreateAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        user_profile = getattr(user, 'userprofile', None)
        isAdmin = user_profile.role == 'admin' if user_profile else False
        if isAdmin:
            return Child.objects.all()
        return Child.objects.filter(parent=user)
    
    def perform_create(self, serializer):
        user = self.request.user
        user_profile = getattr(user, 'userprofile', None)
        isParent = user_profile.role == 'user' if user_profile else False
        print(f"User profile: {user_profile.role}")  # print the user profile for debugging
        if not isParent:
            raise PermissionDenied('Forbidden: Only parents can create children.')
        
        if serializer.is_valid():
            serializer.save(parent=self.request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ManyExpertiseCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # get expertise for userprofile admin only
    def get(self, request):
        # Only allow users with role 'admin' to view expertise
        expertises = Expertise.objects.all()
        serializer = ExpertiseSerializer(expertises, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # post expertise
    def post(self, request):
        user_profile = getattr(request.user, 'userprofile', None)
        if not user_profile or user_profile.role != 'admin':
            return Response({'detail': 'Forbidden: Only admin can create expertise.'}, status=403)

        expertise_list = request.data.get("expertise")
        if not isinstance(expertise_list, list):
            return Response({'detail': 'Expected "expertise" to be a list of strings.'}, status=400)

        data = [{"expertise": expertise} for expertise in expertise_list]

        serializer = ExpertiseSerializer(data=data, many=True)
        if serializer.is_valid():
            expertises = [item['expertise'] for item in serializer.validated_data]

            # Avoid duplicates
            existing_expertises = set(
                Expertise.objects.filter(expertise__in=expertises).values_list('expertise', flat=True)
            )
            new_expertise = [
                Expertise(expertise=expertise) for expertise in expertises if expertise not in existing_expertises
            ]

            Expertise.objects.bulk_create(new_expertise)

            # Return all (existing + new)
            all_expertise = Expertise.objects.filter(expertise__in=expertises)
            return Response(ExpertiseSerializer(all_expertise, many=True).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# create Therapist
class TherapistListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Note: u're printing for debuging if image exist
        print(f"Request data: {request.data}")
        therapists = Therapist.objects.all().prefetch_related('expertise')
        serializer = TherapistSerializer(therapists, many=True, context={'request': request})
        user_profile = getattr(request.user, 'userprofile', None)
        if not user_profile or user_profile.role != 'admin':
            return Response({'detail': 'Forbidden: Only admin can view therapist.'}, status=403)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        print(f"Request data: {request.data}")
        user_profile = getattr(request.user, 'userprofile', None)
        if not user_profile or user_profile.role != 'admin':
            return Response({'detail': 'Forbidden: Only admin can create therapist.'}, status=403)
    
        if 'image' not in request.FILES:
            return Response({'detail': 'Image is required.'}, status=400)
        
        expertise_ids = request.data.getlist('expertise_ids', [])
        if not expertise_ids:
            return Response({'detail': 'Expertise IDs are required.'}, status=400)
        
        try:
            expertise_objects = Expertise.objects.filter(id__in=expertise_ids)
            if len(expertise_objects) != len(expertise_ids):
                return Response({'detail': 'One or more expertise IDs are invalid.'}, status=400)
        except ValueError:
            return Response({'detail': 'Expertise IDs must be integers.'}, status=400)

        data = request.data.copy()
        data['image'] = request.FILES['image']
        
        serializer = TherapistSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            therapist = serializer.save()
            therapist.expertise.set(expertise_objects)
            
            response_serializer = TherapistSerializer(therapist, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# child related
class LanguageListCreate(generics.ListCreateAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Language.objects.all()
    
    def create(self, request, *args, **kwargs):
        languages = request.data.get('languages', [])
        if not isinstance(languages, list):
            return Response({'detail': 'Expected "languages" to be a list of strings.'}, status=400)
        
        created_languages = []
        for lang in languages:
            serializer = self.get_serializer(data={'languages': lang})
            if serializer.is_valid():
                language = serializer.save()
                created_languages.append(language)
            else:
                return Response(serializer.errors, status=400)
            
        return  Response(self.get_serializer(created_languages, many=True).data, status=201)
    
# concerns
class ConcernListCreate(generics.ListCreateAPIView):
    serializer_class = ChildConcernSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Concern.objects.all()
    
    def create(self, request, *args, **kwargs):
        concerns = request.data.get('concerns', [])
        if not isinstance(concerns, list):
            return Response({'detail': 'Expected "concerns" to be a list of objects.'}, status=400)
        
        serializer = self.get_serializer(data=concerns, many=True)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
# Therapist Match
class TherapistMatchListCreate(generics.ListCreateAPIView):
    serializer_class = TherapistMatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_profile = getattr(user, 'userprofile', None)
        is_admin = user_profile.role == 'admin' if user_profile else False

        if is_admin:
            return TherapistMatch.objects.all()
        else:
            return TherapistMatch.objects.filter(child__parent=user)

    def perform_create(self, serializer):
        user = self.request.user
        user_profile = getattr(user, 'userprofile', None)
        is_admin = user_profile.role == 'admin' if user_profile else False

        if is_admin:
            instance = serializer.save()
        else:
            child = serializer.validated_data.get('child')
            if child.parent != user:
                raise PermissionDenied("You do not have permission to assign this child.")
            instance = serializer.save()

        # WebSocket notification for new TherapistMatch
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "therapistmatch",
            {
                "type": "therapistmatch_created",
                "data": TherapistMatchNestedSerializer(instance).data,
            },
        )

class TherapistMatchRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TherapistMatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_profile = getattr(user, 'userprofile', None)
        is_admin = user_profile.role == 'admin' if user_profile else False
        if is_admin:
            return TherapistMatch.objects.all()
        else:
            return TherapistMatch.objects.filter(child__parent=user)

    def update(self, request, *args, **kwargs):
        user_profile = getattr(request.user, 'userprofile', None)
        if not user_profile or user_profile.role != 'user':
            return Response({'detail': 'Forbidden: Only parents can accept or decline.'}, status=403)
        return super().update(request, *args, **kwargs)