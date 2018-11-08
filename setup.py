import os
from setuptools import find_packages, setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='python-snipeit-client',
    version='0.1.0',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    license='MIT',
    install_requires=[
        'django>=2.1.0,<2.2',
        'django-classified',
        'requests==2.20.0',
        'click==7.0'
    ],
    entry_points={
        'console_scripts': [
            'snipeit-client = snipeit.commands:cli',
        ],
    },
    author_email='pkucmus@gmail.com',
    tests_require=['parameterized'],
)
