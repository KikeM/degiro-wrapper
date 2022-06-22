from setuptools import setup, find_packages

setup(
    name="degiro-wrapper",
    install_requires=[
        "click",
        "openpyxl",
        "pandas",
        "QuantStats",
        "tqdm",
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "degiro = degiro_wrapper.cli.cli:cli",
        ],
    },
)
