from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='privledge',
      version='0.1',
      description='Private, Privleged Ledger',
      long_description=readme(),
      url='https://github.com/elBradford/privledge',
      author='Bradford',
      packages=['privledge'],
      install_requires=[
          'sshpubkeys',
          'python-daemon',
          'termcolor',
          'Crypto',
      ],
      entry_points={
          'console_scripts': ['pls=privledge.main:main'],
      },
      zip_safe=False)
