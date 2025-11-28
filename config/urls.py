from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as users_views

urlpatterns = [
    path("", include("presente.urls")),
    path("users/", include("users.urls")),
    # Third party
    # Override allauth views to add SUAP user restrictions
    path(
        "accounts/email/",
        users_views.CustomEmailView.as_view(),
        name="account_email",
    ),
    path(
        "accounts/password/change/",
        users_views.CustomPasswordChangeView.as_view(),
        name="account_change_password",
    ),
    path("accounts/", include("allauth.urls")),
    path("tinymce/", include("tinymce.urls")),
    path("admin/", admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
