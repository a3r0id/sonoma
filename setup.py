import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sonoma",
    version="1.0.8",
    author="hostinfodev",
    author_email="support@host-info.net",
    description="A tiny, programmable http-server crafting framework that is built with security and simplicity in mind.",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hostinfodev/sonoma",
    packages=["sonoma"],
    include_package_data=True,
    #install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers"
    ],
    python_requires='>=3.6',
)