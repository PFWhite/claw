from setuptools import setup

setup(name='claw',
      version='1.0.0',
      description='The Claw - Used to download remote files via SFTP',
      url='http://github.com/devmattm/claw',
      author='Matthew McConnell',
      author_email='devmattm@gmail.com',
      license='MIT',
      packages=['claw'],
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'claw = claw.claw:main',
          ],
      },
      install_requires=['docopt', 'pyyaml', 'pysftp'],
      zip_safe=False)
