from setuptools import setup, find_packages

setup(
    name='esg-cli',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click', 'legendary-gl', 'python-resize-image', 'requests', 'vdf'
    ],
    entry_points={
        'console_scripts': [
            'esg = esg.scripts.main:cli',
        ],
    },
)
