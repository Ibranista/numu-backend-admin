from django.urls import path
# for media

from . import views

urlpatterns = [
    path("notes/", views.NoteListCreate.as_view(), name="note-list-create"),
    path("notes/delete/<int:pk>/", views.NoteDelete.as_view(), name="note-delete"),
    path("children/", views.ChildListCreate.as_view(), name="children-list-create" ),
    path("user/profile/<str:firebase_uid>/", views.UserDetailsView.as_view(), name="user-details"),
    path("expertise/", views.ManyExpertiseCreateView.as_view(), name="expertise-many-create"),
    path("therapist/", views.TherapistListCreate.as_view(), name="therapist-list-create"),
    path("language/", views.LanguageListCreate.as_view(), name="language-list-create"),
    path("concerns/", views.ConcernListCreate.as_view(), name="concerns-list-create"),
    path("therapistsMatch/", views.TherapistMatchListCreate.as_view(), name="therapist-match-list-create"),
    path("therapistsMatch/<int:pk>/", views.TherapistMatchRetrieveUpdateDestroy.as_view(), name="therapist-match-detail"),
]