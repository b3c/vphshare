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
    install_requires=['django>=1.3.1', 'oauth2>=1.5.167', 'python_openid>=2.2', 'django-social-auth', 'suds', 'pysimplesoap', 'django-piston','M2Crypto','pycrypto','mod-auth-library', 'requests', 'lxml==2.3.6'],
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
