from setuptools import setup

setup(
    name="masonite-entry",
    version='0.1.2',
    packages=[
        'entry',
        'entry.api',
        'entry.api.models',
        'entry.commands',
        'entry.migrations',
        'entry.providers',
    ],
    install_requires=[
        'masonite>=1.5,<= 1.5.99',
    ],
    include_package_data=True,
)
