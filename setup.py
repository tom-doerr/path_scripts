from setuptools import setup, find_packages

setup(
    name="path-scripts",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich>=13.9.4",  # Ensure we have the right version of rich
        "litellm",
        "textual>=0.1.18",  # Use the version that's already installed
    ],
    scripts=['bin/agent'],
    entry_points={
        'console_scripts': [
            'agent-cli=src.interface.cli:main',
        ],
    },
)
