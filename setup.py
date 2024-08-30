from setuptools import setup, find_packages

setup(
    name="fastapi-g-context",
    version="0.0.1",
    description="fastapi-g-context is a Python module that provides a simple mechanism for managing \
    global variables with context isolation in FastAPI applications. \
        It is designed to ensure that each request operates within its own isolated context, \
            preventing data leakage between requests.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/chrisK824/fastapi-g-context",
    author="Chris Karvouniaris",
    author_email="christos.karvouniaris247@gmail.com",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "starlette"
    ],
    python_requires=">=3.7",
    license="MIT",
    license_files=["LICENSE"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
