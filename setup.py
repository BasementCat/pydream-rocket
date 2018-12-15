import os

from setuptools import setup

# Using vbox, hard links do not work
if os.environ.get('USER','') == 'vagrant':
    del os.link

with open('README.md', 'r') as fp:
    longdesc = fp.read()

setup(
    name='pydream_rocket',
    version='0.2.0',
    description='Control DreamCheeky USB rocket launchers',
    long_description=longdesc,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
    ],
    url='https://github.com/BasementCat/pydream-rocket',
    author='Alec Elton',
    author_email='alec.elton@gmail.com',
    license='',
    packages=['pydream_rocket'],
    install_requires=['pyusb', 'bottle'],
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False
)