[[_TOC_]]

## `pytest.ini`
Create custom behavioral, external, and performance test markers:

```
[pytest]
markers =
    behavioral: Behavioral (e.g. not unit) tests
    external: Relies on an external resource (e.g. Azure)
    performance: Performance tests
```

## `setup.cfg`

Configure the various tools we use, as well as the overall library:

```
[metadata]
name = {{ cookiecutter.project_name }}
version = attr: {{ cookiecutter.project_name }}.__version__
license = MIT
author = {{ cookiecutter.project_name }}
author_email = {{ cookiecutter.author_email }}
maintainer = {{ cookiecutter.author_email }}
maintainer_email = {{ cookiecutter.author_email }}
description = Library for {{ cookiecutter.project_name }}.
long_description = file: README.md
long_description_content_type = text/x-md
classifiers =
    Development Status :: 2 - Pre-Alpha
    Environment :: Web Environment
    Intended Audience :: Developers
    Operating System :: OS Independent
    Programming Language :: Python

[options.entry_points]
console_scripts =
    {{ cookiecutter.project_name }} = {{ cookiecutter.project_name }}.main:cli

[tool:pytest]
testpaths = tests
filterwarnings =
    error

[coverage:run]
branch = True
source =
    flask
    tests

[coverage:paths]
source =
    {{ cookiecutter.project_name }}

[flake8]
# B = bugbear
# E = pycodestyle errors
# F = flake8 pyflakes
# W = pycodestyle warnings
# B9 = bugbear opinions
# ISC = implicit-str-concat
select = B, E, F, W, B9, ISC
ignore =
    W503 # line break before binary operator
    E203 # : inside of a list slice
    E501 # Line too long
# up to 88 allowed by bugbear B950
max-line-length = 120

[isort]
profile = black

[mypy]
files = {{ cookiecutter.project_name }}
python_version = 3.8
allow_redefinition = True
disallow_subclassing_any = True
# disallow_untyped_calls = True
# disallow_untyped_defs = True
# disallow_incomplete_defs = True
no_implicit_optional = True
local_partial_types = True
# no_implicit_reexport = True
strict_equality = True
warn_redundant_casts = True
warn_unused_configs = True
warn_unused_ignores = True
# warn_return_any = True
# warn_unreachable = True
ignore_missing_imports = True
```

## `setup.py`

Create the Python library:
```python
from setuptools import find_packages, setup

# Metadata goes in setup.cfg. These are here for git dependency graph.
with open("requirements.txt") as f:
    requires = f.read().splitlines()
with open("requirements_dev.txt") as f:
    dev_requires = f.read().splitlines()

setup(
    name="{{ cookiecutter.project_name }}",
    install_requires=requires,
    setup_requires=requires,
    extras_require={"dev": dev_requires},
    packages=find_packages(),
    python_requires=">= 3.8",
)
```

## `pyproject.toml`

Set black line length to 120:

```
[tool.black]
line-length=120
```