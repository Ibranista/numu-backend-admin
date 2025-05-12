# Note: these are just routes like your express app.
from django.urls import path

from . import views

urlpatterns = [
    path("children/", views.ChildListCreate.as_view(), name="children-list-create" ),
    path("user/profile/<str:firebase_uid>/", views.UserDetailsView.as_view(), name="user-details"),
    path("expertise/", views.ManyExpertiseCreateView.as_view(), name="expertise-many-create"),
    path("therapist/", views.TherapistListCreate.as_view(), name="therapist-list-create"),
    path("language/", views.LanguageListCreate.as_view(), name="language-list-create"),
    path("concerns/", views.ConcernListCreate.as_view(), name="concerns-list-create"),
    path("therapistsMatch/", views.TherapistMatchListCreate.as_view(), name="therapist-match-list-create"),
    path("therapistsMatch/<int:pk>/", views.TherapistMatchRetrieveUpdateDestroy.as_view(), name="therapist-match-detail"),
]