try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

#!/usr/bin/env python
from setuptools import setup, find_packages
import scs

METADATA = dict(
    name='vphshare-masterinterface',
    version=scs.__version__,
    author='Matteo Balasso',
    author_email='m.balasso@scsitaly.com',
    description='VphShare Master Interface Django Project',
    long_description=open('../README.rst').read(),
    url='http://github.com/b3c/vphshare',
    keywords='django openid registration github vphshare',
    install_requires=['django<=1.4.5', 'oauth2==1.5.167', 'python_openid<=2.2.5', 'django-social-auth<=0.6.9', 'suds<=0.4', 'pysimplesoap<=1.05a', 'django-piston<=0.2.3','M2Crypto<=0.21.1','pycrypto<=2.6','mod-auth-library', 'requests<=1.2.0', 'lxml<=2.3.6', 'ordereddict<=1.1','django-workflows<=1.0.2','django-permissions<=1.0.3', 'xmltodict<=0.8.6','django-datetime-widget<=0.9.2', 'django_select2<=4.2.2', 'celery<=3.1.9', 'django-celery<=3.1.1', 'raven', 'django-paintstore', 'jsonpath-rw'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Environment :: Web Environment',
        'Topic :: Internet',
        'Operating System :: OS Independent',
        'Programming Language :: Python 2.6',
        'Framework :: Django',
        ],
    zip_safe=False,
    packages=find_packages(),
)

if __name__ == '__main__':
    setup(**METADATA)
