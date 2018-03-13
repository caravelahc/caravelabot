from setuptools import setup, find_packages


setup(
    name='caravelabot',
    packages=find_packages(),
    install_requires=['python-telegram-bot', 'dataset'],
    entry_points={
        'console_scripts': [
            'caravelabot = caravelabot.bot:main',
        ],
    },
)
