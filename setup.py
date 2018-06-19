from setuptools import setup

setup(
    name="masonite-entry",
    version='1.0.0',
    packages=[
        'entry',
        'entry.api',
        'entry.api.models',
        'entry.commands',
        'entry.migrations',
        'entry.providers',
    ],
    install_requires=[],
    include_package_data=True,
)
