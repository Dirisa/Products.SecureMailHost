from setuptools import setup, find_packages

version = '1.1.2'

setup(name='Products.SecureMailHost',
      version=version,
      description="SecureMailHost is a reimplementation of the standard Zope2 "
                  "MailHost with some security and usability enhancements.",
      long_description="""\
      """,
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
      download_url='http://plone.org/products/securemailhost/releases',
      install_requires=[
        'setuptools',
      ],
)
