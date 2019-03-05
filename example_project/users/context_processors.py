from django.conf import settings


def social_app_keys(request):
    return {
        'facebook_key': settings.SOCIAL_AUTH_FACEBOOK_KEY,
        'googleoauth2_key': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
    }
