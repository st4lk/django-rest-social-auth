import os
from setuptools import setup, find_packages
from rest_social_auth import __author__, __version__


def __read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


install_requires = __read('requirements.txt').split()

setup(
    name='rest_social_auth',
    author=__author__,
    author_email='alexevseev@gmail.com',
    version=__version__,
    description='Django rest framework resources for social auth',
    long_description=__read('README.rst'),
    platforms=('Any'),
    packages=find_packages(),
    install_requires=install_requires,
    keywords='django social auth rest login signin signup oauth'.split(),
    include_package_data=True,
    license='BSD License',
    package_dir={'rest_social_auth': 'rest_social_auth'},
    url='https://github.com/st4lk/django-rest-social-auth',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
