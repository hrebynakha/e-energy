from setuptools import setup
from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as f:
    logn_desc = f.read()

setup(
    name='energybot',
    version='1.1',
    description='You personal assistant',
    long_description=logn_desc,
    long_description_content_type='text/markdown',
    url='https://github.com/hrebynakha/e-energy.git',
    author='A. Hrebynakha',
    author_email='hrebynakha@gmail.com',
    license='MIT',
    packages=find_namespace_packages(),
    install_requires=['markdown','beautifulsoup4','pyTelegramBotAPI'],
    entry_points={'console_scripts': ['energybot = energybot.bot:main']}
)