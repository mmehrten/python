## `FROM`
Images should pull from the appropriate minimal base image - e.g. should use `python:3.8-alpine` minimal base image in most cases.

## Minimal size

Dockerfiles should minimize image size - this means any time a package is installed with `apt` or `yum` or `pip` care should be taken to ensure that the cache is either not used or cleaned after install:

```docker
FROM python:3.8

RUN pip3 install invoke && pip3 cache purge
```

## Example Dockerfile for a Python Library with CLI

```docker
FROM python:3.8

RUN pip3 install invoke
RUN mkdir /{{ cookiecutter.project_name }}
COPY {{ cookiecutter.project_name }}/ /{{ cookiecutter.project_name }}/{{ cookiecutter.project_name }}/
COPY tasks.py setup.py *.cfg configurations/ *.txt {{ cookiecutter.project_name }}/
WORKDIR /{{ cookiecutter.project_name }}
# Invoke install installs Python packages, so clean pip cache here
RUN invoke install && pip3 cache purge
ENTRYPOINT ["{{ cookiecutter.project_name }}", "--help"]
```