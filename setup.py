import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mincfg",
    version="0.1.0",
    author="biowpn",
    description="Implementation of a minimal Context-Free Grammar recognizer builder.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biowpn/MinimalCFG",
    packages=setuptools.find_packages()
)
