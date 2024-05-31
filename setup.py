from setuptools import setup, find_packages

setup(
    name='nested',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        # Add any dependencies required by your project here
    ],
    entry_points={
        'console_scripts': [
            'nst=nested.main:main',
        ],
    },
    author='Your Name',
    author_email='your@email.com',
    description='A description of your project',
    url='https://github.com/yourusername/nested',
)