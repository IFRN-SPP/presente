from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/add", views.UserCreateView.as_view(), name="user_add"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user_view"),
    path("users/<int:pk>/update/", views.UserUpdateView.as_view(), name="user_change"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user_delete"),
    path("users/profile", views.UserProfileView.as_view(), name="user_profile"),
    path(
        "users/profile/update/",
        views.UserProfileUpdateView.as_view(),
        name="user_profile_change",
    ),
]
