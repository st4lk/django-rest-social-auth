rest_social_auth release notes
==============================

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
