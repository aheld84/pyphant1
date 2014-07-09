# quicktour/setup.py
from setuptools import setup, find_packages

setup(
    name="quicktour",
    version=0.1,
    install_requires=[
        'pyphant',
        'numpy'
        ],
    packages=find_packages(),
    entry_points="""
    [pyphant.workers]
    myentry = quicktour
    """
    )
