def save_avatar(strategy, details, user=None, *args, **kwargs):
    """Get user avatar from social provider."""
    if user:
        changed = False
        backend_name = kwargs['backend'].__class__.__name__.lower()
        response = kwargs.get('response', {})
        if 'facebook' in backend_name:
            if 'id' in response:
                social_thumb = ("http://graph.facebook.com/{0}/picture?"
                    "type=normal").format(response['id'])
                if user.social_thumb != social_thumb:
                    user.social_thumb = social_thumb
                    changed = True
        if changed:
            strategy.storage.user.changed(user)
