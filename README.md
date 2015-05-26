Django REST social auth
=======================

[![Build Status](https://travis-ci.org/st4lk/django-rest-social-auth.png?branch=master)](https://travis-ci.org/st4lk/django-rest-social-auth) [![Coverage Status](https://coveralls.io/repos/st4lk/django-rest-social-auth/badge.png?branch=master)](https://coveralls.io/r/st4lk/django-rest-social-auth?branch=master) [![pypi](https://pypip.in/d/solid_i18n/badge.png)](https://crate.io/packages/solid_i18n/)

OAuth signin with django rest framework.


Requirements
-----------

- python (2.6, 2.7, 3.4)
- django (1.6, 1.7, 1.8)
- djangorestframework (3.1)

Release notes
-------------

[Here](https://github.com/st4lk/django-rest-social-auth/blob/master/RELEASE_NOTES.md)


Motivation
----------

To have a resource, that will do very simple thing:
take the oauth code from social provider (for example facebook)
and return the authenticated user.
That's it.

I can't find such package for [django rest framework](http://www.django-rest-framework.org/).
There are packages, that take access_token, not the code.
Also, i've used to work with awesome package [python-social-auth](https://github.com/omab/python-social-auth),
so it will be nice to use it again. In fact, most of the work is done by this package.
Current util brings a little help to integrate djangorestframework and python-social-auth.

Quick start
-----------

1. Install this package to your python distribution:

        pip install rest-social-auth

2. Do the settings

    Install apps

        INSTALLED_APPS = (
            ...
            'social.apps.django_app.default',  # python social auth
            'rest_framework',
            'rest_framework.authtoken',  # only if you use token authentication
            'rest_social_auth',
        )

    python-social-auth settings, look [documentation](http://psa.matiasaguirre.net/docs/configuration/django.html) for more details

        SOCIAL_AUTH_FACEBOOK_KEY = 'your app client id'
        SOCIAL_AUTH_FACEBOOK_SECRET = 'your app client secret'
        SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', ]  # optional
        SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'locale': 'ru_RU'}  # optional


        AUTHENTICATION_BACKENDS = (
            'social.backends.facebook.FacebookOAuth2',
            # and maybe some others ...
            'django.contrib.auth.backends.ModelBackend',
        )

3. Include rest social urls

    2.1 [session authentication](http://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication)

        url(r'^api/login/', include('rest_social_auth.urls_session')),

    2.2 [token authentication](http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)

        url(r'^api/login/', include('rest_social_auth.urls_token')),

4. You are ready to login users.

    3.1 session authentication

    - /api/login/social/session/

        input:

            {
                "provider": "faceboook",
                "code": "AQBPBBTjbdnehj51"
            }

        output:

            {
                "username": "Alex",
                "email": "user@email.com",
                // other user data
            }

            + session id in cookies

    3.2 token authentication

    - /api/login/social/token/

        input:

            {
                "provider": "faceboook",
                "code": "AQBPBBTjbdnehj51"
            }

        output:

            {
                "token": "68ded41d89f6a28da050f882998b2ea1decebbe0"
            }

    - /api/login/social/token_user/

        input:

            {
                "provider": "faceboook",
                "code": "AQBPBBTjbdnehj51"
            }

        output:

            {
                "username": "Alex",
                "email": "user@email.com",
                // other user data
                "token": "68ded41d89f6a28da050f882998b2ea1decebbe0"
            }

    User model is taken from [`settings.AUTH_USER_MODEL`](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model).


List of oauth providers
-----------------------

Currently only OAuth 2.0 providers are supported.
Look [python-social-auth](https://github.com/omab/python-social-auth#user-content-auth-providers) for full list.
Name of provider is taken from corresponding `backend.name` property of
particular backed class in python-social-auth.

For example for [facebook backend](https://github.com/omab/python-social-auth/blob/master/social/backends/facebook.py#L19)
we see:

        class FacebookOAuth2(BaseOAuth2):
            name = 'facebook'

Here are some provider names:

Provider  | provider name
--------- | -------------
Facebook  | facebook
Google    | google-oauth2
Vkontakte | vk-oauth2
Instagram | instagram
Github    | github
Yandex    | yandex-oauth2


OAuth 2.0 workflow with rest-social-auth
-----------------------------------------
1. Front-end need to know follwoing params for each social provider:
    - client_id  _# id of registered application on social service provider_
    - redirect_uri  _# to this url social provider will redirect with code_
    - scope=your_scope  _# for example email_
    - response_type=code  _# same for all oauth2.0 providers_

2. Front-end redirect user to social authorize url with params from previous point.

3. User confirms.

4. Social provider redirects back to `redirect_uri` with param `code` and possibly `state`, if it was given at point 2. Front-end better check, that state is the same (generate random state at every request in point 2).

5. Front-end now ready to login the user. For this, send POST request with all params from point 3. + provider name:

        POST /api/login/social/session/

    with data (form data or json)

        provider=facebook&code=AQBPBBTjbdnehj51

    Backend will either signin the user, either signup, either return error.


rest-social-auth purpose
------------------------

As we can see, our backend must implement resource for signin the user (point 5).

Django REST social auth provides means to easily implement these resource.



Customization
-------------

First of all, all customization avaliable by python-social-auth is also avaliable.
For example, use nice concept of [pipeline](http://psa.matiasaguirre.net/docs/pipeline.html) to do any action you need during login/signin.

Second, you can override any method from current package.
You can specify serializer for each view or by subclassing the view.

To do it

- define your own url:

        url(r'^api/login/social/$', MySocialView.as_view(), name='social_login'),

- define your serializer

        from rest_framework import serializers
        from django.contrib.auth import get_user_model

        class MyUserSerializer(serializers.ModelSerializer):

            class Meta:
                model = get_user_model()
                exclude = ('password', 'user_permissions', 'groups')

- finally define view

        class SocialSessionAuthView(BaseSocialAuthView):
            serializer_class_out = MyUserSerializer


Example
-------

Checkout [example project](https://github.com/st4lk/django-rest-social-auth/tree/master/example_project).

- download it

        git clone https://github.com/st4lk/django-rest-social-auth.git

- step in example_project/

        cd django-rest-social-auth/example_project

- create database (sqlite3)

        python manage.py syncdb

- run development server

        python manage.py runserver

Example project already contains facebook app id and secret.
This app is configured to work only with restsocialexample.com domain.
So, to play with it, define in you [hosts](http://en.wikipedia.org/wiki/Hosts_\(file\)) file this domain as localhost:

    127.0.0.1       restsocialexample.com

And visit http://restsocialexample.com:8000/
