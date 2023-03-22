import glob
import os

from invoke import task

PROJECT = "{{ cookiecutter.project_slug }}"
REQUIRED_TEST_COV_PCT = 100
EXCLUDE_FILES = (
    "*dist/*",
    "*poetry.lock*",
    "*tests/*",
    "*templates/*",
    "*examples/*",
    "*__pycache__/*",
    "*.mypy_cache/*",
)


@task
def clean(c):
    """Remove all files not tracked by git."""
    c.run("git clean -Xdf", echo=True)


@task
def build_docs(c):
    """Build project documentation with sphinx."""
    c.run("sphinx-build docs docs/_build", echo=True)


def _install(
    c,
    clear_cache: bool,
    is_dev: bool = True,
):
    if is_dev:
        c.run(f"pip install --editable '.[dev]'", echo=True)
    else:
        c.run(f"pip install .", echo=True)

    if clear_cache:
        # Work around old pip versions erroring on cache purge
        c.run(
            "pip cache purge || echo 'pip cache purge failed, older pip version'",
            echo=True,
        )
    c.run("cp git_hooks/* .git/hooks || echo 'Failed to install git hooks'", echo=True)


install_help = {
    "clear-cache": "Clear the poetry cache",
}


@task(help=install_help)
def develop(
    c,
    clear_cache=False,
):
    """Install module with development packages included."""
    c.run("pip install -r requirements_build.txt", echo=True)
    _install(c, clear_cache=clear_cache, is_dev=True)


@task(help=install_help)
def install(
    c,
    clear_cache=False,
):
    """Install production package for module without development packages included."""
    c.run("pip install -r requirements_build.txt", echo=True)
    _install(c, clear_cache=clear_cache, is_dev=False)


@task(
    help={
        "tag": "Image tag to use",
    }
)
def build_docker(c, tag=None):
    """Build docker image for module."""
    args = []
    if tag:
        args += ["-t", tag]
    args.append(".")
    c.run(f"docker build {' '.join(args)}")


def _build_targz(c):
    excludes = " --exclude ".join(f"'{i}'" for i in EXCLUDE_FILES)
    to_package = " ".join((f"{PROJECT}/", "*.txt", "*.cfg", "*.py"))
    package_name = f"{PROJECT}.tar.gz"
    c.run(
        f"tar --exclude {excludes} -czvf {package_name} {to_package}",
        echo=True,
    )
    print(f"Code staged in {package_name}")


@task
def build_targz(c):
    """Package {{ cookiecutter.project_slug }} code as a tar.gz file."""
    _build_targz(c)


@task
def build_lambdas(c):
    """Package lambdas into zip files, installing requirements.txt into a package/ directory, if they exist."""
    artifacts = []
    c.run("rm -r python || echo ''", echo=True)
    c.run("rm -r tmp || echo ''", echo=True)
    zip_dir = os.path.abspath("tmp/lambda_zips/")
    if not os.path.exists(zip_dir):
        os.makedirs(zip_dir)
    excludes = " --exclude ".join(
        (
            "",
            *(f"'{i}'" for i in EXCLUDE_FILES),
        )
    )
    # Create a new venv to package our environment into
    # Lambda layers require path to be python/ based: https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path
    c.run("python -m venv python", echo=True)
    c.run(
        "source python/bin/activate && pip install -r requirements_build.txt",
        echo=True,
    )
    # Install modules that are required for Lambda functions to run
    c.run(
        f"source python/bin/activate && invoke install",
        echo=True,
    )
    # Copy {{ cookiecutter.project_slug }} source code into virtual env directory required for Lambda
    c.run(
        f"cp -r {PROJECT} python/lib/python3.8/site-packages/{PROJECT}/",
        echo=True,
    )
    # Make .pth files point to /opt in Lambda instead of local directory location
    c.run(
        f"sed -i.bak 's#.*{PROJECT}/libs#/opt/python/lib/python3.8/site-packages/{PROJECT}/libs#' python/lib/python3.8/site-packages/{PROJECT}_*.pth"
    )
    c.run(
        f"sed -i.bak 's#.*{PROJECT}/projects#/opt/python/lib/python3.8/site-packages/{PROJECT}/projects#' python/lib/python3.8/site-packages/{PROJECT}_*.pth"
    )

    # Package the zip file and deploy to S3 / layer
    zip_file = f"{zip_dir}/{PROJECT}-deps.zip"
    c.run(
        f"zip {excludes} -r {zip_file} python/lib/python3.8/site-packages",
        echo=True,
    )
    artifacts.append(zip_file)

    # Publish each function as its own zip package
    for l_dir in glob.glob("lambda/*"):
        if not os.path.exists(f"{l_dir}/lambda_function.py"):
            print(
                f"{l_dir}/lambda_function.py file not found. Lambda file must have this name."
            )
            continue

        zip_file = f"{zip_dir}/{l_dir.split('/')[-1]}.zip"
        # Install any function-specific requirements into the zip directory
        if os.path.exists(f"{l_dir}/requirements.txt"):
            c.run(
                f"pip install --target ./package -r {l_dir}/requirements.txt", echo=True
            )
            c.run(f"cd package && zip {excludes} -r {zip_file} .", echo=True)
            c.run("rm -r package", echo=True)
        # Package and publish the lambda
        c.run(
            f"cd {l_dir} && zip {excludes} -g {zip_file} lambda_function.py", echo=True
        )
        artifacts.append(zip_file)
    print("Lambda artifact locations:")
    for artifact in artifacts:
        print(artifact)


@task
def check(c):
    """Check code format and typing for all modules."""
    path_list = f"{PROJECT} tests/"
    c.run(f"flake8 {PROJECT}", echo=True)
    c.run(f"isort --check {path_list}", echo=True)
    c.run(f"black --check {path_list}", echo=True)
    c.run(f"mypy {PROJECT}", echo=True)


@task
def format(c):
    """Format code according to project standards."""
    path_list = f"{PROJECT} tests/"
    c.run(
        "autoflake "
        + path_list
        + " -r "
        + "--remove-all-unused-imports "
        + "--remove-unused-variables "
        + "-i",
        echo=True,
    )
    c.run(f"isort {path_list}", echo=True)
    c.run(f"black {path_list}", echo=True)


@task
def test(c, x=False, failed_first=False, verbose=True, no_cov=False):
    """Run unit tests."""
    args = []
    if not no_cov:
        args += [
            f"--cov {PROJECT}",
            f"--cov-fail-under {REQUIRED_TEST_COV_PCT}",
            "--cov-report term-missing ",
            "--cov-config ./setup.cfg ",
        ]
    args.append("-m 'not behavioral and not external and not performance'")
    if verbose:
        args.append("-vvv")
    if x:
        args.append("-x")
    if failed_first:
        args.append("--failed-first")
    args_str = " ".join(args)
    c.run(f"pytest {args_str} tests/")


@task
def test_behavioral(c, verbose=True):
    """Run behavioral tests."""
    args = [f"--cov {PROJECT}", "-m 'not performance'"]
    if verbose:
        args.append("-vvv")
    args_str = " ".join(args)
    c.run(f"pytest {args_str} tests/")


@task
def test_performance(c, verbose=True):
    """Run performance tests."""
    args = [f"--cov {PROJECT}", "-m 'not behavioral and not external'"]
    if verbose:
        args.append("-vvv")
    args_str = " ".join(args)
    c.run(f"pytest {args_str} tests/")
