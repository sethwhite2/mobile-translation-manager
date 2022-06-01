from setuptools import setup, find_packages

setup(
    name="mobile_translation_manager",
    description="A library that aims to simplify managing translations for iOS and Android applications.",
    long_description="A library that aims to simplify managing translations for iOS and Android applications.",
    version="0.0.3",
    author='Seth White',
    author_email="flying.squirrel.development@gmail.com",
    keywords='translations localizations android ios manager manage simplify simple strings string language languages app apps applicaiton applications',
    url='https://github.com/sethwhite2/mobile-translation-manager',
    license="MIT",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'lxml',
        'munch',
        'marshmallow',
        'gspread',
    ]
)