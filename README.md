Django REST social auth
=======================

[![Lint](https://github.com/st4lk/django-rest-social-auth/actions/workflows/lint.yml/badge.svg?branch=master)](https://github.com/st4lk/django-rest-social-auth/actions/workflows/lint.yml?query=branch%3Amaster)
[![Tests](https://github.com/st4lk/django-rest-social-auth/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/st4lk/django-rest-social-auth/actions/workflows/test.yml?query=branch%3Amaster)
[![Coverage Status](https://coveralls.io/repos/github/st4lk/django-rest-social-auth/badge.svg?branch=master)](https://coveralls.io/github/st4lk/django-rest-social-auth?branch=master)
[![Pypi version](https://img.shields.io/pypi/v/rest_social_auth.svg)](https://pypi.python.org/pypi/rest_social_auth)
[![Downloads](https://pepy.tech/badge/rest-social-auth)](https://pepy.tech/project/rest-social-auth)


OAuth signin with django rest framework.


Requirements
-----------

- python (3.7, 3.8, 3.9, 3.10)
- django (3.2, 4.1)
- djangorestframework (>=3.9, <4.0)
- social-auth-core (>=4.3, <5.0)
- social-auth-app-django (>=5.0, <6.0)
- [optional] djangorestframework-simplejwt (>=5.0.0)
- [optional] django-rest-knox (>=4.0.0, <5.0.0)

Release notes
-------------

[Here](https://github.com/st4lk/django-rest-social-auth/blob/master/RELEASE_NOTES.md)


Motivation
----------

To have a resource, that will do very simple thing:
take the [oauth code](https://tools.ietf.org/html/rfc6749#section-1.3.1) from social provider (for example facebook)
and return the authenticated user.
That's it.

I can't find such util for [django rest framework](http://www.django-rest-framework.org/).
There are packages (for example [django-rest-auth](https://github.com/Tivix/django-rest-auth)), that take [access_token](https://tools.ietf.org/html/rfc6749#section-1.4), not the [code](https://tools.ietf.org/html/rfc6749#section-1.3.1).
Also, i've used to work with awesome library [python-social-auth](https://github.com/omab/python-social-auth),
so it will be nice to use it again (now it is split into [social-core](https://github.com/python-social-auth/social-core) and [social-app-django](https://github.com/python-social-auth/social-app-django)). In fact, most of the work is done by this package.
Current util brings a little help to integrate django-rest-framework and python-social-auth.

Quick start
-----------

1. Install this package to your python distribution:

    ```bash
    pip install rest-social-auth
    ```

2. Do the settings


    Install apps

    ```python
    INSTALLED_APPS = (
        ...
        'rest_framework',
        'rest_framework.authtoken',  # only if you use token authentication
        'social_django',  # django social auth
        'rest_social_auth',  # this package
        'knox',  # Only if you use django-rest-knox
    )
    ```

    social auth settings, look [documentation](http://python-social-auth.readthedocs.io/en/latest/configuration/django.html) for more details

    ```python
    SOCIAL_AUTH_FACEBOOK_KEY = 'your app client id'
    SOCIAL_AUTH_FACEBOOK_SECRET = 'your app client secret'
    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', ]  # optional
    SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'locale': 'ru_RU'}  # optional


    AUTHENTICATION_BACKENDS = (
        'social_core.backends.facebook.FacebookOAuth2',
        # and maybe some others ...
        'django.contrib.auth.backends.ModelBackend',
    )
    ```

    Also look [optional settings](#settings) avaliable.

3. Make sure everything is up do date

    ```bash
    python manage.py migrate
    ```


4. Include rest social urls (choose at least one)

    4.1 [session authentication](http://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication)

    ```python
    path('api/login/', include('rest_social_auth.urls_session')),
    ```

    4.2 [token authentication](http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)

    ```python
    path('api/login/', include('rest_social_auth.urls_token')),
    ```

    4.3 [jwt authentication](https://github.com/davesque/django-rest-framework-simplejwt)

    ```python
    path('api/login/', include('rest_social_auth.urls_jwt_pair')),
    ```

    or / and

    ```python
    path('api/login/', include('rest_social_auth.urls_jwt_sliding')),
    ```

    4.4 [knox authentication](https://github.com/James1345/django-rest-knox/)

    ```python
    path('api/login/', include('rest_social_auth.urls_knox')),
    ```

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

    5.3 jwt authentication (using [django-rest-framework-simplejwt](https://github.com/davesque/django-rest-framework-simplejwt))

    - POST /api/login/social/jwt-pair/
    - POST /api/login/social/jwt-pair-user/

        Similar to token authentication, but token is JSON Web Token.

        See [JWT.io](http://jwt.io/) for details.

        To use it, django-rest-framework-simplejwt must be installed.

        For `jwt-pair`, the response will include additional "refresh" token:
        ```json
        {
            "token": "...",
            "refresh": "..."
        }
        ```

        ##### Or sliding JWT token:

    - POST /api/login/social/jwt-sliding/
    - POST /api/login/social/jwt-sliding-user/

        Check [docs of simplejwt](https://github.com/davesque/django-rest-framework-simplejwt#token-types) for pair/sliding token difference.

        Note. `django-rest-framework-simplejwt` doesn't work on python3.6

    5.4 knox authentication

    - POST /api/login/social/knox/
    - POST /api/login/social/knox_user/

        Similar to token authentication, but token is Django Rest Knox Token.

        To use it, [django-rest-knox](https://github.com/James1345/django-rest-knox/) must be installed.


    User model is taken from [`settings.AUTH_USER_MODEL`](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model).

    At input there is also non-required field `redirect_uri`.
    If given, server will use this redirect uri in requests, instead of uri
    got from settings.
    This redirect_uri must be equal in front-end request and in back-end request.
    Back-end will not do any redirect in fact.

    It is also possible to specify provider in URL, not in request body.
    Just append it to the url:

        POST /api/login/social/session/facebook/

    Don't need to specify it in body now:

        {
            "code": "AQBPBBTjbdnehj51"
        }

    Provider defined in URL has higher priority than provider in body.
    If both are specified - provider will be taken from URL.


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


rest-social-auth purpose
------------------------

As we can see, our backend must implement resource for signin the user.

Django REST social auth provides means to easily implement such resource.


List of oauth providers
-----------------------

OAuth 1.0 and OAuth 2.0 providers are supported.

Look [python-social-auth](http://python-social-auth.readthedocs.io/en/latest/backends/index.html#social-backends) for full list.
Name of provider is taken from corresponding `backend.name` property of
particular backed class in python-social-auth.

For example for [facebook backend](https://github.com/python-social-auth/social-core/blob/master/social_core/backends/facebook.py#L22)
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
[Others](http://python-social-auth.readthedocs.io/en/latest/backends/index.html#social-backends) | [...](http://python-social-auth.readthedocs.io/en/latest/backends/index.html#social-backends)


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

- `REST_SOCIAL_LOG_AUTH_EXCEPTIONS`

    Default: `True`

    When `False` will not log social auth authentication exceptions.

- `REST_SOCIAL_VERBOSE_ERRORS`

    Default: `False`

    When `True` the API will return error message received from server. Can be potentially unsecure to turn it ON.

- `SOCIAL_AUTH_STRATEGY`

    Default: `'rest_social_auth.strategy.DRFStrategy'`

    Override [strategy](https://python-social-auth.readthedocs.io/en/latest/strategies.html) for python-social-auth.


Customization
-------------

First of all, customization provided by python-social-auth is also avaliable.
For example, use nice mechanism of [pipeline](http://python-social-auth.readthedocs.io/en/latest/pipeline.html) to do any action you need during login/signin.

Second, you can override any method from current package.
Specify serializer for each view by subclassing the view.

To do it

- define your own url:

        path('api/login/social/$', MySocialView.as_view(), name='social_login'),

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

- clone repo

    ```bash
    git clone https://github.com/st4lk/django-rest-social-auth.git
    ```

- run example project

    ```bash
    make
    ```

    It is assumed, that you have:
    - [make](https://www.gnu.org/software/make/)
    - [docker](https://www.docker.com/)

- open [https://127.0.0.1:8000/](https://127.0.0.1:8000/) in your browser

    Note: `runsslserver` is used instead of built-in `runserver` to serve the project with TLS (aka SSL) certificate.
    HTTPS is required by some social providers (facebook), without it they won't work.
    The certificate will not be trusted by your system - that is expected.
    Just tell your browser to proceed with this untrusted certificate - it is acceptable for development purposes.

    In Chrome browser it can look like this:
    - step 1: [image](https://user-images.githubusercontent.com/1771042/71641969-90ab7280-2cd6-11ea-95ed-de4c6e123345.png)
    - step 2: [image](https://user-images.githubusercontent.com/1771042/71641970-91440900-2cd6-11ea-9275-f6c351ddc543.png)

    More details [here](https://github.com/teddziuba/django-sslserver#browser-certificate-errors).

Facebook, Google and Twitter auth should work, all secret keys are already set.

Example project uses [satellizer](https://github.com/sahat/satellizer) angularjs module.

Development
-----------

Run tests locally

```bash
make test
```

Run tests in all enviroments (can take some time)

```bash
make test-tox
```

Contributors
------------

Thanks to all contributors!

<a href="https://github.com/st4lk/django-rest-social-auth/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=st4lk/django-rest-social-auth" />
</a>

- Alexey Evseev, [st4lk](https://github.com/st4lk)
- James Keys, [skolsuper](https://github.com/skolsuper)
- Aaron Abbott, [aabmass](https://github.com/aabmass)
- Grigorii Eremeev, [Budulianin](https://github.com/Budulianin)
- shubham, [shubh3794](https://github.com/shubh3794)
- Deshraj Yadav, [DESHRAJ](https://github.com/DESHRAJ)
- georgewhewell, [georgewhewell](https://github.com/georgewhewell)
- Ahmed Sa3d, [zee93](https://github.com/zee93)
- Olle Vidner, [ovidner](https://github.com/ovidner)
- MounirMesselmeni, [MounirMesselmeni](https://github.com/MounirMesselmeni)
- Tuomas Virtanen, [katajakasa](https://github.com/katajakasa)
- Jeremy Storer, [storerjeremy](https://github.com/storerjeremy)
- Jeffrey de Lange, [jgadelange](https://github.com/jgadelange)
- John Vandenberg, [jayvdb](https://github.com/jayvdb)
- Anton_Datsik, [AntonDatsik](https://github.com/AntonDatsik)
- Netizen29, [Netizen29](https://github.com/Netizen29)
- Dipendra Raj Panta, [Mr-DRP](https://github.com/Mr-DRP)
- JD, [jd-0001](https://github.com/jd-0001)
- Harsh Patel, [eelectronn](https://github.com/eelectronn)
- Devid, [sevdog](https://github.com/sevdog)
- Anton Yakovlev, [sputnik5459](https://github.com/sputnik5459)
- Olivér Kecskeméty, [KOliver94](https://github.com/KOliver94)
- vainu-arto, [vainu-arto](https://github.com/vainu-arto)
