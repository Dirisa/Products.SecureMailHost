import os
from setuptools import setup, find_packages

name = 'Products.SecureMailHost'
version = '2.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.txt')
    )

setup(name=name,
      version=version,
      description="SecureMailHost is a reimplementation of the standard Zope2 "
                  "MailHost with some security and usability enhancements.",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
      ],
      keywords='Zope Plone Secure Mail Host',
      author='Christian Heimes',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/collective/SecureMailHost/trunk',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
)
