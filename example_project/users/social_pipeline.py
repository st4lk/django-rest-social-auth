import hashlib


def auto_logout(*args, **kwargs):
    """Do not compare current user with new one"""
    return {'user': None}


def save_avatar(strategy, details, user=None, *args, **kwargs):
    """Get user avatar from social provider."""
    if user:
        backend_name = kwargs['backend'].__class__.__name__.lower()
        response = kwargs.get('response', {})
        social_thumb = None
        if 'facebook' in backend_name:
            if 'id' in response:
                social_thumb = ("http://graph.facebook.com/{0}/picture?"
                    "type=normal").format(response['id'])
        else:
            social_thumb = "http://www.gravatar.com/avatar/"
            social_thumb += hashlib.md5(user.email.lower()).hexdigest()
            social_thumb += "?size=100"
        if social_thumb and user.social_thumb != social_thumb:
            user.social_thumb = social_thumb
            strategy.storage.user.changed(user)
