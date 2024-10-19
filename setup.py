from setuptools import setup, find_packages

setup(
    name="nested",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "rich>=10.0.0",
        "click>=7.0",
        "prompt_toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "nst=nested.main:main",
        ],
    },
    author="Your Name",
    author_email="your@email.com",
    description="A description of your project",
    url="https://github.com/yourusername/nested",
)
