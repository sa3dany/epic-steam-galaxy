import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='esg-cli',
    version='0.0.1',
    description='Adds GOG & EGL games to Steam as shortcuts.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='epic, steam, galaxy, cli',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],

    packages=find_packages(),
    install_requires=[
        'click', 'legendary-gl', 'python-resize-image', 'requests', 'vdf'
    ],
    entry_points={
        'console_scripts': [
            'esg = esg.scripts.main:cli',
        ],
    },
)
