import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

requires = [
    'pyramid >= 1.5a1',
    'deform >= 2.0a2',
    'pyramid_layout',
    'six',
    ]

setup(name='pyramid_admin2',
      version='0.3',
      description='pyramid_admin2',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Hoc .T Do',
      author_email='hoc3010@gmail.com',
      url='https://github.com/tarzanjw/pyramid_admin2',
      keywords='web wsgi bfg pylons pyramid',
      packages=['pyramid_admin2', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      )