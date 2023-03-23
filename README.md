# Python Boilerplates

This repository contains a sample projects with boilerplate to handle
different use cases. Currently it focuses on automating common
development tasks like linting, type checking, installing packages,
building Docker images, etc.

## Usage

This repository uses [cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.2/)
to create new projects for their use cases. We recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/) for package management. Generally speaking, these projects assume **python 3.8 or later**.

```bash
$ python -m venv default
$ source default/bin/activate
$ pip install cookiecutter invoke
$ cookiecutter "https://github.com/mmehrten/python.git" --directory "cookiecutters/python_core"
```

From there, you can see the project-specific READMEs for further instructions.

## Projects

### python_core

A library to help with common development tasks. Includes documentation
for project standards as well.

```
invoke develop
invoke install
invoke format
invoke check
invoke test
invoke test-behavioral
invoke test-performance
invoke build-docs
invoke build-docker
invoke build-lambdas
invoke build-targz
```