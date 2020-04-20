from setuptools import setup, find_packages


setup(
    name="degiro-wrapper",
    install_requires=[
        "QuantStats",
        "tqdm",
        "xlrd",
        "pandas",
        "numpy",
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
)
