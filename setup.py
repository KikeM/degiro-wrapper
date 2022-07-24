from setuptools import setup, find_packages
import versioneer

setup(
    name="degiro-wrapper",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        "click",
        "matplotlib",
        "numpy",
        "openpyxl",
        "pandas",
        "requests",
        "tqdm",
        # "QuantStats",
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "degiro = degiro_wrapper.cli.cli:cli",
        ],
    },
)
