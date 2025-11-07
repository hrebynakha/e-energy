"""Setup file for build package"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="energybot",
    version="1.1.0",
    author="Anatolii Hrebynakha",
    author_email="hrebynakha@gmail.com",
    description="Your personal assistant bot",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/hrebynakha/e-energy",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "markdown",
        "beautifulsoup4",
        "pyTelegramBotAPI",
    ],
    entry_points={
        "console_scripts": [
            "energybot=energybot.bot:main",
        ]
    },
    python_requires=">=3.8",
)
