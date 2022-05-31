import os
import sys
from setuptools import setup
from rest_social_auth import __author__, __version__


def __read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except OSError:
        return ''


if sys.argv[-1] == 'build':
    os.system('python setup.py sdist')
    os.system('python setup.py bdist_wheel')


if sys.argv[-1] == 'publish':
    # TODO: Need python 3.4.6+, 3.5.3+, Python 3.6+ here, add a check
    # https://packaging.python.org/guides/migrating-to-pypi-org/#uploading
    dists_to_upload = [
        f'dist/rest_social_auth-{__version__}.tar.gz',
        f'dist/rest_social_auth-{__version__}-py2.py3-none-any.whl',
    ]
    for dist in dists_to_upload:
        print(f'Uploading {dist}')
        os.system(f'twine upload -r pypi {dist}')
    sys.exit()


if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system(f"git tag -a v{__version__} -m 'version {__version__}'")
    os.system("git push --tags")
    sys.exit()


install_requires = __read('requirements.txt').split()

setup(
    name='rest_social_auth',
    author=__author__,
    author_email='alexevseev@gmail.com',
    version=__version__,
    description='Django rest framework resources for social auth',
    long_description=__read('README.md') + '\n\n' + __read('RELEASE_NOTES.md'),
    long_description_content_type='text/markdown; charset=UTF-8',
    platforms=('Any'),
    packages=['rest_social_auth'],
    install_requires=install_requires,
    keywords='django social auth rest login signin signup oauth'.split(),
    include_package_data=True,
    license='MIT license',
    package_dir={'rest_social_auth': 'rest_social_auth'},
    url='https://github.com/st4lk/django-rest-social-auth',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities',
    ],
)
