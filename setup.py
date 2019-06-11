import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
description = "Asynchronous SMTP server for local development and email testing"
github_homepage = "https://github.com/asyncee/smtpdev"
long_description = f"""
{description}

See source code and documentation on {github_homepage}.
"""
requirements = open(os.path.join(here, "requirements.txt")).readlines()


data_files = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)


# This code snippet is taken from django-registration setup.py script
for dirpath, dirnames, filenames in os.walk("smtpdev"):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith("."):
            del dirnames[i]
    if filenames:
        prefix = dirpath[len("smtpdev/") :]  # Strip "smtpdev/" or "smtpdev\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(
    name="smtpdev",
    version="0.1.3",
    packages=find_packages(),
    author="asyncee",
    description=description,
    long_description=long_description,
    license="MIT",
    keywords="smtp developer server",
    url=github_homepage,
    download_url="https://pypi.python.org/pypi/smtpdev/",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    package_dir={"smtpdev": "smtpdev"},
    package_data={"smtpdev": data_files},
    zip_safe=False,
    install_requires=requirements,
    entry_points="""
        [console_scripts]
        smtpdev=smtpdev.cli:main
    """,
)
