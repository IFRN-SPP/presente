from django.urls import path
from .views import IndexView

app_name = "presente"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
]
