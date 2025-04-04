from setuptools import setup, find_packages

setup(
    name="path-scripts",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich<13.0.0,>=12.6.0",  # Compatible with textual 0.1.18
        "litellm",
        "textual==0.1.18",  # Pin to the installed version
        "lxml",  # For better XML handling
        "requests",  # For web search
    ],
    entry_points={
        "console_scripts": [
            "agent=src.interface.cli:main",
        ],
    },
)
