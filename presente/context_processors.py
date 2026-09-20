from django.conf import settings


def app_info(request):
    return {
        "app_version": settings.APP_VERSION,
        "git_sha": settings.GIT_SHA,
        "is_dev_build": settings.IMAGE_TAG == "dev",
    }
