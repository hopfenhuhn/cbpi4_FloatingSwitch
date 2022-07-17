from setuptools import setup

setup(name='cbpi4_FloatingSwitch',
      version='0.0.1',
      description='CraftBeerPi Plugin',
      author='Matthias Hansen',
      author_email='cbpi4@hopfenhuhn.de',
      url='',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4_FloatingSwitch': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4_FloatingSwitch'],
     )
