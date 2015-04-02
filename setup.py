try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'M-Blocks',
    'author': 'Sebastian Claici',
    'url': 'https://github.com/sebastian-claici/M-Blocks',
    'download_url': 'https://github.com/sebastian-claici/M-Blocks',
    'author_email': 'sclaici@mit.edu',
    'version': '0.1',
    'install_requires': ['networkx', 'pyserial', 'numpy', 'nose'],
    'packages': ['MBlocks']
    'scripts': [],
    'name': 'MBlocks'
}

setup(**config)
