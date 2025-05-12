# Note: a serializer is a class that helps communicate between incoming data like JSON and Django models. 
# Note: a serializer can be used to validate and serialize data.

from django.contrib.auth.models import User
import firebase_admin.auth
from rest_framework import serializers
from firebase_admin import auth
from .models import Note, Child, UserProfile, Expertise, Therapist, Concern, TherapistMatch
from api.child_serializers.children_serializers import ChildConcernSerializer
import firebase_admin
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["id","username","password"]
#         extra_kwargs = {"password":{"write_only":True}}

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user
    
# Note: avoid drf seralizer for firebase user. (prev is called drf it'll be handled for you.)
class FirebaseUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.ChoiceField(choices=['user', 'admin'], default='user')

    def create(self, validated_data):
        print(f"Creating user with data: {validated_data}")
        try:
            role = validated_data.pop('role', 'user')
            try:
                firebase_user = auth.get_user_by_email(validated_data['email'])
                print(f"User found in Firebase: {firebase_user.uid}")
            except firebase_admin.auth.UserNotFoundError:
                print(f"User not found in Firebase, creating new user: {validated_data['email']}")
                firebase_user = auth.create_user(
                    email=validated_data['email'],
                    password=validated_data['password']
                )

            user, created = User.objects.get_or_create(
                username=firebase_user.uid,
                defaults={
                    'email': firebase_user.email,
                    'first_name': validated_data['first_name'],
                    'last_name': validated_data['last_name']
                }
            )

            if not created:
                user.email = firebase_user.email
                user.first_name = validated_data['first_name']
                user.last_name = validated_data['last_name']
                user.save()

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'firebase_uid': firebase_user.uid,
                    'role': role
                    }
            )

            return {
                "uid": firebase_user.uid,
                "role": role,
                "email": firebase_user.email,
                "first_name": validated_data['first_name'],
                "last_name": validated_data['last_name']
            }

        except Exception as e:
            raise serializers.ValidationError(str(e))

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "created_at", "author"]
        extra_kwargs = {"author":{"read_only":True}}

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = request.user
        return super().create(validated_data)

# user profile serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["firebase_uid", "role"]

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'userprofile']

class ChildSerializer(serializers.ModelSerializer):
    #  tells Django REST Framework (DRF) that the parent field on the 
    # serialized output should not come directly from 
    # a model field — instead, it should come from a custom method 
    # called get_parent.
    parent = serializers.SerializerMethodField()
    concerns = ChildConcernSerializer(many=True, read_only=True)
    therapist_matches = serializers.SerializerMethodField()
    acceptedTherapists = serializers.SerializerMethodField()

    concern_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Concern.objects.all(),
        source='concerns'
    )
    class Meta:
        model = Child
        fields = [
            "id", "name", "gender", "birthDate", "parent", "concern_ids", "concerns", "therapist_matches", "acceptedTherapists"
        ]

    def get_parent(self, obj):
        request = self.context.get("request")
        user_profile = getattr(request.user, 'userprofile', None)
        is_admin = user_profile and user_profile.role == 'admin'
        print(f"all objdata: {obj.parent}")
        if (is_admin):
            return UserSerializer(obj.parent).data
        return obj.parent.id

    def create(self, validated_data):
        concerns = validated_data.pop("concerns", [])
        child = super().create(validated_data)
        child.concerns.set(concerns)
        return child

    def get_therapist_matches(self, obj):
        matches = obj.therapist_matches.all()
        return TherapistMatchNestedSerializer(matches, many=True, context=self.context).data

    def get_acceptedTherapists(self, obj):
        accepted_matches = obj.therapist_matches.filter(status='accepted')
        return [TherapistSerializer(match.therapist, context=self.context).data for match in accepted_matches]

class ExpertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expertise
        fields = ["id", "expertise"]
        extra_kwargs = {"id": {"read_only": True}}

class TherapistSerializer(serializers.ModelSerializer):
    expertise = ExpertiseSerializer(many=True, read_only=True)
    expertise_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Expertise.objects.all(),
        source='expertise'
        # source is what model field or property this serializer field is representing
        # my therapist model has a field called expertise
    )
    
    # upload image fix
    image = serializers.ImageField()

    class Meta:
        model = Therapist
        fields = ["id", "name", "image", "expertise", "expertise_ids", "experience_years", "bio", "createdDate"]
        extra_kwargs = {
            "id": {"read_only": True},
            "createdDate": {"read_only": True}
        }

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     request = self.context.get('request')
    #     if rep.get('image') and request:
    #         rep['image'] = request.build_absolute_uri(rep['image'])
    #     return rep

class TherapistMatchSerializer(serializers.ModelSerializer):
    child = serializers.PrimaryKeyRelatedField(queryset=Child.objects.all())
    therapist = serializers.PrimaryKeyRelatedField(queryset=Therapist.objects.all())

    class Meta:
        model = TherapistMatch
        fields = [
            'id', 'child', 'therapist', 'status', 'decline_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        child = data.get('child')
        therapist = data.get('therapist')
        if TherapistMatch.objects.filter(child=child, therapist=therapist).exists():
            raise serializers.ValidationError('A match between this child and therapist already exists.')
        return data

class TherapistMatchNestedSerializer(serializers.ModelSerializer):
    therapist = TherapistSerializer(read_only=True)
    class Meta:
        model = TherapistMatch
        fields = [
            'id', 'therapist', 'status', 'decline_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
