## invoke

Invoke is a tool to make a command-line automation tool easily, in an organized way, in native Python. This is an improvement over shell scripts because it allows us to call arbitrary Python code without the need for extensive scripting, and organizes a variety of CLI behaviors into one script rather than many.

Install with:

```bash
pip install invoke
```

Then define the CLI methods with a `tasks.py` file:

```python
import glob

from invoke import task

@task
def develop(c):
    c.run("pip3 install --editable .[dev]")


@task
def install(c):
    c.run("pip3 install .")


@task
def check(c):
    items = glob.glob("func*")
    path_list = " ".join(items)
    c.run("flake8 {{ cookiecutter.project_name }} " + path_list)
    c.run("isort --check {{ cookiecutter.project_name }} " + path_list)
    c.run("black --check {{ cookiecutter.project_name }} " + path_list)
    c.run("mypy {{ cookiecutter.project_name }} " + path_list)


@task
def format(c):
    items = glob.glob("func*")
    c.run(
        "autoflake {{ cookiecutter.project_name }} "
        + " ".join(items)
        + " -r "
        + "--remove-all-unused-imports "
        + "--remove-unused-variables "
        + "-i"
    )

    items = glob.glob("func*/*.py", recursive=True) + glob.glob("{{ cookiecutter.project_name }}/*.py", recursive=True)
    c.run("isort {{ cookiecutter.project_name }} tests " + " ".join(items))
    c.run("black {{ cookiecutter.project_name }} tests " + " ".join(items))
```

We now have an automation CLI that we can operate with:

```
invoke develop
invoke format
invoke check
invoke install
invoke --help
```

You can also use the shorthand `inv` rather than `invoke` - e.g. `inv format`


## IDEs

You can configure PyCharm to run `black`, `isort`, and `autoflake` when you save a file:

* [black](https://black.readthedocs.io/en/stable/integrations/editors.html)
* [isort](https://github.com/PyCQA/isort/issues/258#issuecomment-95675882)
* autoflake - follow same process as isort

## Git hooks

You can configure git hooks to run arbitrary shell scripts when you commit, push, etc. For example, you could place the following script in `.git/hooks/pre-push`:

```
#!/bin/bash
set -ex
invoke check test
```

This would ensure that your code formatted is checked & correct, and that your tests are passing, before you're allowed to push. (note: You can override the hook and push anyways with `git push --force`)

Similarly, you could put the following script in `.git/hooks/pre-commit`:

```
#!/bin/bash
set -ex
invoke format check
```

This would ensure that your code is always formatted correctly before you commit.