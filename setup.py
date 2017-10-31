from setuptools import setup, find_packages
from perch import __version__


setup(
    name='perch security',
    version=__version__,
    author='Nick Hagianis',
    author_email='dev@perchsecurity.com',
    url='https://github.com/usePF/perch-client',
    packages=find_packages(exclude=['tests', 'examples']),
    include_package_data=True,
    license='MIT',
    description='Perch Security python client and command line tools',
    long_description='Perch Security python client and command line tools',
    install_requires=['click', 'requests'],
    entry_points='''
        [console_scripts]
        perch=perch.cli:cli
    ''',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
