Django REST social auth
=======================

[![Build Status](https://travis-ci.org/st4lk/django-rest-social-auth.svg?branch=master)](https://travis-ci.org/st4lk/django-rest-social-auth)
[![Coverage Status](https://coveralls.io/repos/st4lk/django-rest-social-auth/badge.svg?branch=master)](https://coveralls.io/r/st4lk/django-rest-social-auth?branch=master)
[![Pypi version](https://img.shields.io/pypi/v/rest_social_auth.svg)](https://pypi.python.org/pypi/rest_social_auth)


OAuth signin with django rest framework.


Requirements
-----------

- python (2.7, 3.4, 3.5)
- django (1.7, 1.8, 1.9)
- djangorestframework (>= 3.1)
- python-social-auth (>=0.2.9)
- [optional] djangorestframework-jwt (>=1.7.2)

Release notes
-------------

[Here](https://github.com/st4lk/django-rest-social-auth/blob/master/RELEASE_NOTES.md)


Motivation
----------

To have a resource, that will do very simple thing:
take the oauth code from social provider (for example facebook)
and return the authenticated user.
That's it.

I can't find such util for [django rest framework](http://www.django-rest-framework.org/).
There are packages (for example [django-rest-auth](https://github.com/Tivix/django-rest-auth)), that take access_token, not the code.
Also, i've used to work with awesome library [python-social-auth](https://github.com/omab/python-social-auth),
so it will be nice to use it again. In fact, most of the work is done by this package.
Current util brings a little help to integrate django-rest-framework and python-social-auth.

Quick start
-----------

1. Install this package to your python distribution:

        pip install rest-social-auth

2. Do the settings

    Install apps

        INSTALLED_APPS = (
            ...
            'rest_framework',
            'rest_framework.authtoken',  # only if you use token authentication
            'social.apps.django_app.default',  # python social auth
            'rest_social_auth',  # this package
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

    Also look [optional settings](#settings) avaliable.

3. Make sure everything is up do date

        python manage.py migrate


4. Include rest social urls (choose at least one)

    4.1 [session authentication](http://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication)

        url(r'^api/login/', include('rest_social_auth.urls_session')),

    4.2 [token authentication](http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)

        url(r'^api/login/', include('rest_social_auth.urls_token')),

    4.3 [jwt authentication](http://getblimp.github.io/django-rest-framework-jwt/)

        url(r'^api/login/', include('rest_social_auth.urls_jwt')),

5. You are ready to login users

    Following examples are for OAuth 2.0.

    5.1 session authentication

    - POST /api/login/social/session/

        input:

            {
                "provider": "facebook",
                "code": "AQBPBBTjbdnehj51"
            }

        output:

            {
                "username": "Alex",
                "email": "user@email.com",
                // other user data
            }

            + session id in cookies

    5.2 token authentication

    - POST /api/login/social/token/

        input:

            {
                "provider": "facebook",
                "code": "AQBPBBTjbdnehj51"
            }

        output:

            {
                "token": "68ded41d89f6a28da050f882998b2ea1decebbe0"
            }

    - POST /api/login/social/token_user/

        input:

            {
                "provider": "facebook",
                "code": "AQBPBBTjbdnehj51"
            }

        output:

            {
                "username": "Alex",
                "email": "user@email.com",
                // other user data
                "token": "68ded41d89f6a28da050f882998b2ea1decebbe0"
            }

    5.3 jwt authentication

    - POST /api/login/social/jwt/
    - POST /api/login/social/jwt_user/

        Similar to token authentication, but token is JSON Web Token.

        See [JWT.io](http://jwt.io/) for details.

        To use it, [django-rest-framework-jwt](https://github.com/GetBlimp/django-rest-framework-jwt) must be installed.

    User model is taken from [`settings.AUTH_USER_MODEL`](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model).

    At input there is also non-required field `redirect_uri`.
    If given, server will use this redirect uri in requests, instead of uri
    got from settings.
    This redirect_uri must be equal in front-end request and in back-end request.
    Back-end will not do any redirect in fact.

    It is also possible to specify provider in url, not in request body.
    Just append it to the url:

        POST /api/login/social/session/facebook/

    Don't need to specify it in body now:

        {
            "code": "AQBPBBTjbdnehj51"
        }


OAuth 2.0 workflow with rest-social-auth
-----------------------------------------
1. Front-end need to know following params for each social provider:
    - client_id  _# only in case of OAuth 2.0, id of registered application on social service provider_
    - redirect_uri  _# to this url social provider will redirect with code_
    - scope=your_scope  _# for example email_
    - response_type=code  _# same for all oauth2.0 providers_

2. Front-end redirect user to social authorize url with params from previous point.

3. User confirms.

4. Social provider redirects back to `redirect_uri` with param `code`.

5. Front-end now ready to login the user. To do it, send POST request with provider name and code:

        POST /api/login/social/session/

    with data (form data or json)

        provider=facebook&code=AQBPBBTjbdnehj51

    Backend will either signin the user, either signup, either return error.

    Sometimes it is more suitable to specify provider in url, not in request body.
    It is possible, rest-social-auth will understand that.
    Following request is the same as above:

        POST /api/login/social/session/facebook/

    with data (form data or json)

        code=AQBPBBTjbdnehj51

    
OAuth 1.0a workflow with rest-social-auth
-----------------------------------------
1. Front-end needs to make a POST request to your backend with the provider name ONLY:
        
        POST /api/login/social/
        
    with data (form data or json):
    
        provider=twitter

    Or specify provider in url, in that case data will be empty:

        POST /api/login/social/twitter

2. The backend will return a short-lived `oauth_token` request token in the response.  This can be used by the front-end to perform authentication with the provider.

3. User confirms.  In the case of Twitter, they will then return the following data to your front-end:

        {
          "redirect_state":  "...bHrz2x0wy43",
          "oauth_token"   :  "...AAAAAAAhD5u",
          "oauth_verifier":  "...wDBdTR7CYdR"
        }

4. Front-end now ready to login the user. To do it, send POST request again with provider name and the `oauth_token` and `oauth_verifier` you got from the provider:

        POST /api/login/social/

    with data (form data or json)

        provider=twitter&oauth_token=AQBPBBTjbdnehj51&oauth_verifier=wDBdTR7CYdR

    Backend will either signin the user, or signup, or return an error.
    Same as in OAuth 2.0, you can specify provider in url, not in body:

        POST /api/login/social/twitter

This flow is the same as described in [satellizer](https://github.com/sahat/satellizer#-login-with-oauth-10). This angularjs module is used in example project.

#### Note
If you use token (or jwt) authentication and OAuth 1.0, then you still need 'django.contrib.sessions' app (it is not required for OAuth 2.0 and token authentication).
This is because python-social-auth will store some data in session between requests to OAuth 1.0 provider.


rest-social-auth purpose
------------------------

As we can see, our backend must implement resource for signin the user.

Django REST social auth provides means to easily implement such resource.


List of oauth providers
-----------------------

OAuth 1.0 and OAuth 2.0 providers are supported.

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
Twitter   | twitter
[Others](https://github.com/omab/python-social-auth#user-content-auth-providers) | ...


Settings
--------

- `REST_SOCIAL_OAUTH_REDIRECT_URI`

    Default: `'/'`

    Defines redirect_uri. This redirect must be the same in both authorize request (made by front-end) and access token request (made by back-end) to OAuth provider.

    To override the relative path (url path or url name are both supported):

        REST_SOCIAL_OAUTH_REDIRECT_URI = '/oauth/redirect/path/'
        # or url name
        REST_SOCIAL_OAUTH_REDIRECT_URI = 'redirect_url_name'

    Note, in case of url name, backend name will be provided to url resolver as argument.

- `REST_SOCIAL_DOMAIN_FROM_ORIGIN`

    Default: `True`

    Sometimes front-end and back-end are run on different domains.
    For example frontend at 'myproject.com', and backend at 'api.myproject.com'.

    If True, domain will be taken from request origin, if origin is defined.
    So in current example domain will be 'myproject.com', not 'api.myproject.com'.
    Next, this domain will be joined with path from `REST_SOCIAL_OAUTH_REDIRECT_URI` settings.

    To be clear, suppose we have following settings (defaults):

        REST_SOCIAL_OAUTH_REDIRECT_URI = '/'
        REST_SOCIAL_DOMAIN_FROM_ORIGIN = True

    Front-end is running on domain 'myproject.com', back-end - on 'api.myproject.com'.
    Back-end will use following redirect_uri:

        myproject.com/

    And with following settings:

        REST_SOCIAL_OAUTH_REDIRECT_URI = '/'
        REST_SOCIAL_DOMAIN_FROM_ORIGIN = False

    redirect_uri will be:

        api.myproject.com/

    Also look at [django-cors-headers](https://github.com/ottoyiu/django-cors-headers) if such architecture is your case.

- `REST_SOCIAL_OAUTH_ABSOLUTE_REDIRECT_URI`

    Default: `None`

    Full redirect uri (domain and path) can be hardcoded

        REST_SOCIAL_OAUTH_ABSOLUTE_REDIRECT_URI = 'http://myproject.com/'

    This settings has higher priority than `REST_SOCIAL_OAUTH_REDIRECT_URI` and `REST_SOCIAL_DOMAIN_FROM_ORIGIN`.
    I.e. if this settings is defined, other will be ignored.
    But `redirect_uri` param from request has higher priority than any setting.



Customization
-------------

First of all, customization provided by python-social-auth is also avaliable.
For example, use nice mechanism of [pipeline](http://psa.matiasaguirre.net/docs/pipeline.html) to do any action you need during login/signin.

Second, you can override any method from current package.
Specify serializer for each view by subclassing the view.

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

- define view

        from rest_social_auth.views import SocialSessionAuthView
        from .serializers import MyUserSerializer

        class MySocialView(SocialSessionAuthView):
            serializer_class = MyUserSerializer

Check the code of the lib, there is not much of it.


Example
-------

There is an [example project](https://github.com/st4lk/django-rest-social-auth/tree/master/example_project).

- make sure you have rest-social-auth installed

        pip install rest-social-auth

- clone repo

        git clone https://github.com/st4lk/django-rest-social-auth.git

- step in example_project/

        cd django-rest-social-auth/example_project

- create database (sqlite3)

        python manage.py syncdb

- run development server

        python manage.py runserver

Example project already contains facebook, google and twitter app ids and secrets.
These apps are configured to work only with restsocialexample.com domain (localhost is not supported by some providers).
So, to play with it, define in your [hosts](http://en.wikipedia.org/wiki/Hosts_\(file\)) file this domain as localhost:

    127.0.0.1       restsocialexample.com

And visit http://restsocialexample.com:8000/

Example project uses [satellizer](https://github.com/sahat/satellizer) angularjs module.


Contributors
------------

- Alexey Evseev, [st4lk](https://github.com/st4lk)
- James Keys, [skolsuper](https://github.com/skolsuper)
- Aaron Abbott, [aabmass](https://github.com/aabmass)
- Grigorii Eremeev, [Budulianin](https://github.com/Budulianin)
- shubham, [shubh3794](https://github.com/shubh3794)
- Deshraj Yadav, [DESHRAJ](https://github.com/DESHRAJ)
