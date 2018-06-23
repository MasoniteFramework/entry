from setuptools import setup

setup(
    name="masonite-entry",
    version='1.0.7',
    packages=[
        'entry',
        'entry.api',
        'entry.api.models',
        'entry.commands',
        'entry.migrations',
        'entry.providers',
    ],
    install_requires=[
        'PyJWT==1.6.4'
    ],
    include_package_data=True,
)
