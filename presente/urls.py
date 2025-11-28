from django.urls import path
from . import views

app_name = "presente"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("my-activities/", views.MyActivitiesView.as_view(), name="my_activities"),
    path("activity/", views.ActivityListView.as_view(), name="activity_list"),
    path("activity/add", views.ActivityCreateView.as_view(), name="activity_add"),
    path(
        "activity/<int:pk>/", views.ActivityDetailView.as_view(), name="activity_view"
    ),
    path(
        "activity/<int:pk>/update/",
        views.ActivityUpdateView.as_view(),
        name="activity_change",
    ),
    path(
        "activity/<int:pk>/delete/",
        views.ActivityDeleteView.as_view(),
        name="activity_delete",
    ),
    path(
        "activity/<int:pk>/attendances/",
        views.ActivityAttendanceListView.as_view(),
        name="activity_attendances",
    ),
    path(
        "activity/<int:pk>/attendances/print/config/",
        views.ActivityAttendancePrintConfigView.as_view(),
        name="activity_attendance_print_config",
    ),
    path(
        "activity/<int:pk>/attendances/print/",
        views.ActivityAttendancePrintView.as_view(),
        name="activity_attendance_print",
    ),
    path(
        "activity/<int:activity_pk>/attendance/<int:pk>/delete/",
        views.AttendanceDeleteView.as_view(),
        name="attendance_delete",
    ),
    # User attendances
    path("my-attendances/", views.MyAttendancesView.as_view(), name="my_attendances"),
    # Public attendance URLs
    path(
        "a/<str:encoded_id>/",
        views.PublicActivityView.as_view(),
        name="public_activity",
    ),
    path(
        "a/<str:encoded_id>/qr/", views.ActivityQRCodeView.as_view(), name="activity_qr"
    ),
    path("checkin/<str:token>/", views.CheckInView.as_view(), name="checkin"),
]
