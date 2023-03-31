# Best practices for writing tests

## Pick a test framework

Python offers many different test frameworks. I recommend using [pytest](https://docs.pytest.org/en/7.2.x/), 
as it provides the most user-friendly abstractions of the test frameworks I've used. The documentation here will assume that
you're using pytest, although the best practices may overlap between frameworks.

## Unit Testing
Developing software can be thought of as writing a series of "contracts". For example, consider the following function:

```python
def add(left: int, right: int) -> int:
    return left + right
```

This method's contract says "You give me two integers, `left` and `right`, and I'll return you an integer that is the sum of the two you passed."
This method doesn't say anything about what happens if you pass floats or strings. It doesn't explicitly raise any exceptions. It has a prety simple
contract. So, when we write our unit tests for this function, our tests should reflect the contract that we're making.

```python
import pytest

@pytest.mark.parametrize("left, right, expected", [
    (1, 2, 3), (0, 0, 0), (1, -1, 0)
])
def test_add(left, right, expected):
    assert add(left, right) == expected
```

That's it. We don't need to test anything more because we've covered all of the different ways we expect our contract to behave.

Now, let's take a more complex contract:

```python
import boto3
import os
from typing import Dict, Optional
import logging
from botocore.exceptions import ClientError

def upload(path: str, bucket: str, object_name: Optional[str] = None) -> bool:
    """Upload a file to S3.
    
    :param path: The path to the file in the OS
    :param bucket: The S3 bucket to upload to
    :param object_name: The object name in S3. If not provided, will use the file name (excluding the file path prefix)
    :returns: True if the upload succeeds, False if it fails for any reason
    """
    if object_name is None:
        object_name = os.path.basename(path)

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(path, bucket, object_name)
    except ClientError as e:
        logging.error("Failed to upload. Error: %s", e)
        return False
    return True
```

This contains many different cases to test:

1. If the object isn't specified, we use the file name 
2. If any exception is raised at all we don't raise it, and we just log an error
3. We return True on success and False on failures

The core to unit testing is that we're testing the _contract_ we're writing - _not_ the underlying libraries we're using.
We don't actually care about whether or not a file gets uploaded to S3. In fact, we explicitly don't want to upload anything to S3
in reality because that's slow and expensive. We just want to make sure that we're *calling the boto3 APIs correctly*, and know
that as long as we do that, we'll get our file uploaded to S3 in the end.

To do this, we use the concepts of *mocking* and *patching*. Mocking is the act of creating a fake object to represent a real one.
Patching is the act of replacing a real method with a fake one that does what we want it to do instead. In Python, everthing is an object,
even functions, so we can use Mocks both for "normal" objects like classes and for functions. To do this we use a library called `unittest`
which provides mocking functionality via a pytest fixture named `mocker`. pytest also provides us with the ability to test logging functionality with a fixture called `caplog`.

```python
from unittest.mock import sentinel, Mock, call


def test_upload_does_not_raise_errors_on_failure(mocker, caplog):
    mock_s3_client = Mock()
    patch_boto3 = mocker.patch("boto3.client", return_value=mock_s3_client)
    mock_s3_client.upload_file.side_effect = ClientError({}, {})
    
    assert upload(sentinel.path, sentinel.bucket, sentinel.object) is False
    assert patch_boto3.mock_calls == [call("s3")]
    assert mock_s3_client.mock_calls == [call.upload_file(sentinel.path, sentinel.bucket, sentinel.object)]
    assert "Failed to upload. Error:" in caplog.text


def test_upload_returns_true_on_success(mocker, caplog):
    mock_s3_client = Mock()
    patch_boto3 = mocker.patch("boto3.client", return_value=mock_s3_client)
    
    assert upload(sentinel.path, sentinel.bucket, sentinel.object) is True
    assert patch_boto3.mock_calls == [call("s3")]
    assert mock_s3_client.mock_calls == [call.upload_file(sentinel.path, sentinel.bucket, sentinel.object)]
    assert caplog.text == ""


def test_upload_uses_basename(mocker, caplog):
    mock_s3_client = Mock()
    patch_boto3 = mocker.patch("boto3.client", return_value=mock_s3_client)
    patch_os = mocker.patch("os.path.basename", return_value=sentinel.basename)
    
    assert upload(sentinel.path, sentinel.bucket) is True
    assert patch_boto3.mock_calls == [call("s3")]
    assert mock_s3_client.mock_calls == [call.upload_file(sentinel.path, sentinel.bucket, sentinel.basename)]
    assert caplog.text == ""
```

Here we test our contracts in our API, without needing to test the functionalities of the `boto3` or `os` modules. We trust that they have tested their
contracts, and as long as we call their contracts accordingly, they'll do what they say. We can verify that behavior during functional testing and 
end to end testing, where we not only test the contracts but that the actual behavior is as we expect.

A host of pre-configured patches and mocks are developed as pytest fixtures in the cookiecutter. Please refer to [the cookiecutter conftest.py](https://github.com/mmehrten/python/blob/main/cookiecutters/python_core/%7B%7B%20cookiecutter.project_name%20%7D%7D/tests/conftest.py), [the cookiecutter tests](https://github.com/mmehrten/python/tree/main/cookiecutters/python_core/%7B%7B%20cookiecutter.project_name%20%7D%7D/tests) and [the example rendered tests](https://github.com/mmehrten/python/tree/main/examples/python-core-example/tests) for some more unit testing examples.

## Functional Testing
TODO...

## End to End Testing
TODO...

## Performance Testing
TODO...

## When to Test
TODO...

