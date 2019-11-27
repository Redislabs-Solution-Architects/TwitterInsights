from setuptools import setup

setup(
    name='twitter_insights',
    packages=['twitter_insights'],
    include_package_data=True,
    install_requires=[
        'pubnub',
    ],
)
