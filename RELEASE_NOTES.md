rest_social_auth release notes
==============================

master
------

v2.2.0
------
- Update license, use MIT
- Add Django 2.2 support
- Fix customer redirect URI for OAuth1
- Cleanup knox integration

v2.1.0
------
- Use djangorestframework-simplejwt for JWT implementation
- Deprecate djangorestframework-jwt
- Add python3.7 support

Issues: #74

v2.0.2
------
- Make social-auth-core >=3.0 as mandatory dependency 

v2.0.1
------
- Minor update of pypi deployment process

v2.0.0
------
- Update social-auth-core dependency to at least 3.0.0

Issues: #73

v1.5.0
------
- Update minimal required version of social-auth-app-django to 3.1.0
- Minor updates in readme
- Add Django 2.1 support
- Drop Django 1.10 support
- Drop Python 3.4 support

Issues: #70

v1.4.0
------
- Add django-rest-knox support

v1.3.1
------
- Fix Django 2.0 support

v1.3.0
------
- Add Django 2.0 support
- Drop Django 1.8, 1.9 support

Issues: #58

v1.2.0
------
- Add Python 3.6 and Django 1.11 support

Issues #54

v1.1.0
------
- Update docs
- Add new setting `REST_SOCIAL_LOG_AUTH_EXCEPTIONS`

Issues #42

v1.0.0
------
- Add Django 1.10 support
- Drop Django 1.7 support
- Add social-auth-core, social-auth-app-django dependencies
- Drop python-social-auth dependency

Issues: #33, #35, #37, #38

v0.5.0
------
- Handle HttpResponses returned by the pipeline

Issues: #28

v0.4.4
------
- Log exceptions from python-social-auth
- Don't use find_packages from setuptools

Issues: #22, #25

v0.4.3
------
- Fix queryset assert error
- minor typo fixes

Issues: #20

v0.4.2
------
- Remove django.conf.urls.patterns from code
- Exclude modifing immutable data
- refactor tests
- minor typo fixes

Issues: #11, #17, #14

v0.4.1
------
- Fix requirements.txt: allow django==1.9

v0.4.0
------
- Add [JSON Web Tokens](http://jwt.io/) using [djangorestframework-jwt](https://github.com/GetBlimp/django-rest-framework-jwt)
- Add Python 3.5 and Django 1.9 support

Issues: #6

v0.3.1
------
- Explicitly set token authentication for token views

v0.3.0
------
- Add support for Oauth1
- Add ability to override request parsing
- Allow to specify provider in url
- Drop Python 2.6 and Django 1.6 support

Issues: #2, #3, #5

v0.2.0
------
- Get domain from HTTP Origin
- Add example of Google OAuth2.0
- Add manual redirect uri (front-end can specify it)
- Use GenericAPIView instead of APIView
- Main serializer is output serializer, not input
- Update docs
- Minor code fixes

v0.1.0
------

First version in pypi
