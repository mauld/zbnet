from setuptools import setup


setup(name='zbnet',
      version='1.0',
      description='create a zigbee network to control arudinos with simple commands',
      author='Matthew Auld',
      author_email='matthew@matthewauld.ca',
      url='none',
      packages=['zbnet'],
      install_requires=['pyserial>=3.3', 'XBee>=2.2.5'])
