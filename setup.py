from setuptools import setup, find_packages

version = '2.0.dev0'

setup(name='Products.SecureMailHost',
      version=version,
      description="SecureMailHost is a reimplementation of the standard Zope2 "
                  "MailHost with some security and usability enhancements.",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 3.3",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Framework :: Plone :: 5.0",
          "Framework :: Zope2",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.4",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
      ],
      keywords='Zope Plone Secure Mail Host',
      author='Christian Heimes',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://pypi.python.org/pypi/Products.SecureMailHost',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'DateTime',
          'ZODB3',
          'Zope2',
      ],
      )
