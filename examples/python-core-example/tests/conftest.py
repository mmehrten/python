import importlib
from typing import List
from unittest.mock import MagicMock, Mock, sentinel

import munch
import pytest
import python_core_example
from click.testing import CliRunner
from python_core_example.cli import cli

python_core_example.logging.configure_logging("DEBUG")


@pytest.fixture
def patch_manager(mocker, patch_path):
    patch_manager = Mock()

    def patch(path, *args, **kwargs):
        # If the user provided a mock, use that directly
        if args and isinstance(args[0], Mock) and not kwargs:
            to_sub = args[0]
        # Otherwise, create a new mock to use, allowing magic / not magic as needed
        else:
            mock_cls = Mock
            if kwargs.get("is_magic"):
                mock_cls = MagicMock
                del kwargs["is_magic"]
            to_sub = mock_cls(*args, **kwargs)

        mocker.patch(path, to_sub)
        mock_calls_key = path.split(".")[-1]
        setattr(patch_manager, mock_calls_key, to_sub)
        return to_sub

    def patch_object(obj, path, **kwargs):
        if "return_value" not in kwargs:
            kwargs["return_value"] = getattr(sentinel, path)
        to_sub = Mock(**kwargs)
        mocker.patch.object(obj, path, to_sub)
        setattr(patch_manager, path, to_sub)
        return to_sub

    patch_manager.patch = patch
    patch_manager.patch.object = patch_object
    return patch_manager


@pytest.fixture
def mock_configparser(patch_manager, patch_path):
    mock_parser = patch_manager.patch(f"{patch_path}.configparser")
    mock_parser.ConfigParser = Mock(return_value=mock_parser)
    mock_parser.get = Mock(
        side_effect=lambda section, key, **kwargs: getattr(sentinel, key)
    )
    mock_parser.getint = Mock(
        side_effect=lambda section, key, **kwargs: getattr(sentinel, key)
    )
    return mock_parser


@pytest.fixture
def mock_time(patch_manager, patch_path):
    mock_time = patch_manager.patch(f"{patch_path}.time")
    mock_time.time.return_value = sentinel.time
    return mock_time


@pytest.fixture
def mock_secret(patch_manager, patch_path):
    mock_secret = patch_manager.patch(f"{patch_path}.Secret")
    mock_secret.get = Mock(return_value=sentinel.secret_value)
    return mock_secret


@pytest.fixture
def mock_uuid(patch_manager, patch_path):
    mock_uuid = patch_manager.patch(f"{patch_path}.uuid")
    mock_uuid.uuid4 = Mock(return_value=sentinel.uuid4)
    return mock_uuid


@pytest.fixture
def mock_requests_response():
    return Mock(
        text=sentinel.text,
        status_code=sentinel.status_code,
        headers={},
        cookies={
            "csrftoken": sentinel.resp_csrf_token,
            "sessionid": sentinel.resp_session_id,
        },
    )


@pytest.fixture
def mock_requests(patch_manager, patch_path, mock_requests_response):
    mock_requests = patch_manager.patch(f"{patch_path}.requests")
    mock_requests.Session = Mock(return_value=mock_requests)
    mock_requests.get = Mock(return_value=mock_requests_response)
    mock_requests.post = Mock(return_value=mock_requests_response)
    mock_requests.request = Mock(return_value=mock_requests_response)
    mock_requests.headers = {}
    mock_requests.cookies = {}
    return mock_requests


@pytest.fixture
def mock_json(patch_manager, patch_path):
    mock_json = patch_manager.patch(f"{patch_path}.json")
    mock_json.loads = Mock(return_value=sentinel.loads)
    mock_json.dumps = Mock(return_value=sentinel.dumps)
    sentinel.dumps.encode = Mock(return_value=sentinel.dumps_encoded)
    return mock_json


@pytest.fixture
def mock_yaml(patch_manager, patch_path):
    mock = patch_manager.patch(f"{patch_path}.yaml")
    mock.safe_load = Mock(return_value=sentinel.safe_load)
    return mock


@pytest.fixture
def mock_base64(patch_manager, patch_path):
    mock = patch_manager.patch(f"{patch_path}.base64")
    mock.b64decode = Mock(return_value=sentinel.b64decode)
    return mock


@pytest.fixture
def mock_future():
    mock_future = Mock(result=Mock(return_value=sentinel.result))
    return mock_future


@pytest.fixture
def mock_process_pool(patch_manager, patch_path, mock_future):
    mock_pool = patch_manager.patch(
        f"{patch_path}.concurrent.futures.ProcessPoolExecutor", is_magic=True
    )
    mock_pool.return_value = mock_pool
    mock_pool.__enter__ = Mock(return_value=mock_pool)
    mock_pool.__exit__ = Mock()
    mock_pool.submit = Mock(return_value=mock_future)
    return mock_pool


@pytest.fixture
def mock_thread_pool(patch_manager, patch_path, mock_future):
    mock_pool = patch_manager.patch(
        f"{patch_path}.concurrent.futures.ThreadPoolExecutor", is_magic=True
    )
    mock_pool.return_value = mock_pool
    mock_pool.__enter__ = Mock(return_value=mock_pool)
    mock_pool.__exit__ = Mock()
    mock_pool.submit = Mock(return_value=mock_future)
    return mock_pool


@pytest.fixture
def mock_s3_client(patch_manager):
    mock = patch_manager.boto3.s3
    mock.get_object.return_value = {"Body": sentinel.body}
    mock.list_objects.return_value = {"Contents": [{"Key": sentinel.list_objects_key}]}
    return mock


@pytest.fixture
def mock_botocore(patch_manager, patch_path):
    mock_botocore = patch_manager.patch(
        f"{patch_path}.botocore", patch_manager.botocore
    )
    mock_botocore.config.Config.return_value = sentinel.botocore_config
    return mock_botocore


@pytest.fixture
def mock_boto3(patch_manager, patch_path, mock_s3_client):
    mock = patch_manager.patch(f"{patch_path}.boto3", patch_manager.boto3)
    clients = {"s3": mock_s3_client}
    mock.client = Mock(side_effect=lambda k, **kwargs: clients.get(k, getattr(mock, k)))
    return mock


def patch_defaults(mock, name):
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock()
    attrs = set(dir(mock))
    for a in attrs:
        val = getattr(mock, a)
        if isinstance(val, MagicMock):
            val.configure_mock(
                __name__=name,
                __defaults__=(),
                __kwdefaults__={},
                __annotations__={},
                __qualname__=name,
            )


@pytest.fixture
def mock_s3_helpers(patch_manager, patch_path):
    return patch_manager.patch(f"{patch_path}.S3PathManager")


@pytest.fixture
def mock_time_helpers(patch_manager, patch_path):
    return patch_manager.patch(
        f"{patch_path}.timestamp_millis", return_value=sentinel.timestamp_millis
    )


@pytest.fixture
def mock_pandas(patch_manager, patch_path):
    mock = patch_manager.patch(f"{patch_path}.pd")
    mock.DataFrame = MagicMock()
    mock.DataFrame.return_value = mock.DataFrame
    mock.DataFrame.__getitem__.return_value = mock.Series
    mock.Series.tolist.return_value = sentinel.pandas_list
    mock.read_csv.return_value = mock.DataFrame
    mock.DataFrame.shape = MagicMock()
    mock.DataFrame.shape.__getitem__.return_value = sentinel.df_len
    return mock


@pytest.fixture
def mock_spark_session(patch_manager, patch_path):
    mock = patch_manager.patch(f"{patch_path}.SparkSession")

    mock.conf.return_value = mock.conf
    mock.conf.get.return_value = sentinel.config_value

    mock.read = mock.reader
    mock.reader.return_value = mock.reader
    mock.reader.format.return_value = mock.reader

    mock.DataFrame = MagicMock()
    mock.reader.load.return_value = mock.DataFrame
    mock.DataFrame.return_value = mock.DataFrame
    mock.createDataFrame.return_value = mock.DataFrame
    mock.DataFrame.__getitem__.return_value = mock.Column

    df_operations = [
        "join",
        "select",
        "drop",
        "limit",
        "withColumn",
        "withColumnRenamed",
        "agg",
        "filter",
        "fillna",
        "cache",
    ]
    for op in df_operations:
        mock_op = getattr(mock.DataFrame, op)
        mock_op.return_value = mock.DataFrame

    mock.DataFrame.count.return_value = sentinel.num_records
    mock.PandasDataFrame = MagicMock()
    mock.DataFrame.toPandas.return_value = mock.PandasDataFrame

    mock.Row = MagicMock()
    mock.Row.__getitem__.return_value = mock.Row.item
    mock.DataFrame.head.return_value = mock.Row

    mock.DataFrame.write = mock.writer
    mock.writer.return_value = mock.writer
    mock.writer.format.return_value = mock.writer
    mock.writer.mode.return_value = mock.writer

    return mock


@pytest.fixture
def mock_spark_functions(patch_manager, patch_path):
    from pyspark.sql import functions

    # Get all public spark functions -- those that don't start with _ or an uppercase letter
    funcs_to_patch = [
        f for f in dir(functions) if not (f.startswith("_") or f[0].isupper())
    ]
    mock_funcs = Mock()
    for func in funcs_to_patch:
        try:
            patch_manager.patch(f"{patch_path}.{func}", getattr(mock_funcs, func))
            mocked_func = getattr(mock_funcs, func)
            mocked_func.return_value = mocked_func
            mocked_func.alias.return_value = mocked_func.alias
        except Exception:
            pass
    return mock_funcs


@pytest.fixture
def mock_spark_types(patch_manager, patch_path):
    from pyspark.sql import types

    mock_types = Mock()
    # Remove DataType from Spark types we mock so there isn't a collision with our DataType class
    data_types = types.__all__
    data_types.remove("DataType")
    for type in data_types:
        try:
            patch_manager.patch(f"{patch_path}.{type}", getattr(mock_types, type))
            mocked_type = getattr(mock_types, type)
            mocked_type.return_value = mocked_type
        except Exception:
            pass
    return mock_types


@pytest.fixture
def runner_invoke():
    def _invoke(cli_module: str, args: List[str]):
        # Force ingest CLI to get registered
        importlib.import_module(cli_module)
        return CliRunner().invoke(
            cli, args, obj=munch.munchify({"config": {}, "sessions": {}})
        )

    return _invoke
