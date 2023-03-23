# Development Best Practices
Formatting should conform to development best practices, including:

## Type Hints and Type Checking
We follow [PEP 484](https://www.python.org/dev/peps/pep-0484/) for Python type hints. Type hints are expected for all function arguments, inputs, and outputs. See the docstrings section for examples on using type hints.

This allows us to use MyPy for static type checking of our code. This allows us to detect numerous bugs before code is released, and increases code quality overall.

## Docstrings
We follow [PEP 257](https://www.python.org/dev/peps/pep-0257/) for docstring conventions, and [Sphinx](https://www.sphinx-doc.org/en/master/) formatting for parameters, examples, etc. Docstrings are expected for all public functions & classes, as well as all command-line utilities.

Examples:

```python
@dataclass
class DataclassExample:
    """A class demonstrating how to write docstrings for class variables."""

    arg_1: int #: Example of a docstring for a dataclass arg.
    arg_2: str
    """Example of a multiline docstring for a dataclass arg."""

class DocExample:
    """A class to demonstrate documentation formatting.

    The first line of the docstring is a sentence, with more context below after a newline.
    """

    def fn(self, arg_1: int, arg_2: str) -> str:
        """A function with arguments and a return value.
        
        :param arg_1: The first argument, which is used for reasons.
        :param arg_2: The second argument, which is also used.
        :returns: A string, for reasons.
        :raises: A ValueError if you've done something wrong.
        """
```

## Strict Code Formatting
Formatting code is annoying! But, having formatted code improves our readability, and creates a consistent code base. That's why we use automated tools to format our code for us - so that we can write code however we want, and tools will make our code look the way it's supposed to.

The tools we use for code formatting are:

* `black` - uncompromising code formatter, not configurable, just makes your code look the way it should. "Any color you like, as long as it's black"
* `isort` - sorting and formatting inputs
* `autoflake` - detecting unused inputs, variables, etc. and cleaning up code beyond formatting

## Consistent Variable Naming
We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for our code style. This means:

* Using snake_case for file names, variables, and functions
* Using PascalCase for classes
* UPPER_CASE_WITH_UNDERSCORES for constants
* Prefixing private functions and variables with `_`
* 4 space indentation

## Command Line Interfaces
We use [click](https://click.palletsprojects.com/en/8.0.x/) for command line interfaces.

## Object Oriented Development 
We focus on object-oriented development. Code is developed as classes and functions in classes for reusability, modularity, and abstraction. Scripts should not be written - rather, a command-line entrypoint should be used to instantiate and use a class that performs a specific task.

For example, a script to upload a file to S3 might look like:

files.py:
```python
from dataclasses import dataclass
@dataclass
class FileUploader:
    """A helper class to upload files into an S3 bucket."""

    s3_bucket: str  #: The S3 bucket to load files into.

    def upload(self, file_path: str, s3_object_name: Optional[str] = None) -> None:
        """Upload an OS file to S3.
        
        :param file_path: The fully qualified OS path to the file to upload.
        :param s3_object_name: The S3 object name to upload the file as - if not provided the file_path is used.
        """
```

main.py
```python
from .files import FileUploader
import click

@click.command()
@click.option(
    "--file_path",
    type=str,
    help="The OS path of the file to upload.",
    required=True,
)
@click.option(
    "--s3_bucket",
    type=str,
    help="The S3 bucket to upload the file to.",
    required=True,
)
@click.option(
    "--s3_object_name",
    type=str,
    help="The OS path of the file to upload.",
    default=None,
)
def upload_file(file_path: str, s3_bucket: str, s3_object_name: Optional[str]):
    """Upload a file to S3."""
    loader = FileUploader(s3_bucket)
    loader.upload(file_path, s3_object_name)


if __name__ == "__main__":
    upload_file()
```


## Enums Instead of Magic
When a specific set of actions is desired within a function, it's common to use a "magic variable" to control behavior. For example, if a program runs in a strict mode and in a permissive mode, one might use the strings "strict" and "permissive" as function inputs to change the behavior. This is, in general, bad - and difficult to understand and use as a user. It is preferable to use Enums to control behavior where a specific set of options are available. Enums make behavior explicit and obvious, allow documentation of different inputs, and allows type checking to validate that the correct values are provided.

```python
class RunMode(int, enum.Enum):
    PERMISSIVE = 1
    STRICT = 2
```

## Use UTC timestamps with millisecond granularity

Millisecond granularity is way more than enough for our workflows, so we should use UTC timestamps with millisecond granularity wherever timestamps are needed. 

UTC timestamps are preferred to DateTime objects, Timestamp objects, etc.  