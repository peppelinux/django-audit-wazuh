import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# python3 setup.py sdist
# python3 -m twine upload dist/*

setup(
    name='django_audit_wazuh',
    version='v0.6.0',
    packages=find_packages(),
    include_package_data=True,
    license='Apache',
    description="Django Audit",
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/peppelinux/django-audit',
    author='Giuseppe De Marco',
    author_email='giuseppe.demarco@unical.it',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'django>=3.0,<4.0',
    ],
)
