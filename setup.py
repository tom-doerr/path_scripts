from setuptools import setup, find_packages

setup(
    name="path-scripts",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich",
        "litellm",
    ],
    entry_points={
        'console_scripts': [
            'agent=src.agent_main:main',
            'agent-cli=src.interface.cli:main',
        ],
    },
)
