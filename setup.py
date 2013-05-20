from distutils.core import setup

setup(
    name='loft',
    version='1.0.3',
    author='Matt Brewster, Andrew Hosch',
    author_email='matt.brewster@base2s.com, andrew.hosch@base2s.com',
    packages=['loft','loft.conf'],
    package_data={'': ['LoftLogConfig']},
    data_files=[('/etc/init.d', ['init.d/loft'])],
    description='Logging Filter Transport',
    long_description=open('README.txt').read(),
    requires=['requests'],
    install_lib='/ijet/',
    )
