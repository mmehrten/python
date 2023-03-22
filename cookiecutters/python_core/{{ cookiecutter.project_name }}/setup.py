from setuptools import find_packages, setup

# Metadata goes in setup.cfg. These are here for git dependency graph.
with open("requirements.txt") as f:
    requires = f.read().splitlines()
with open("requirements_dev.txt") as f:
    dev_requires = f.read().splitlines()

setup(
    name="{{ cookiecutter.project_slug }}",
    install_requires=requires,
    setup_requires=requires,
    packages=find_packages(),
    extras_require={"dev": dev_requires},
    python_requires=">= 3.8",
)
