from datetime import date
from unittest.mock import MagicMock

import pytest
from chalice.app import BadRequestError, Chalice, Request

from chalicelib.validation import (
    ValidationParam,
    validate_payload,
    validate_query_params,
)


def test_basic_types_valid():
    mock_request = MagicMock(spec_set=Request)
    mock_log = MagicMock()
    mock_app = MagicMock(Chalice)
    mock_app.current_request = mock_request
    mock_app.log = mock_log

    # valid, required and present
    mock_request.json_body = {
        "int": 1,
        "float": 123.45,
        "str": "hello world",
        "bool": True,
    }

    specs = [
        ValidationParam("int", field_type=int, required=True),
        ValidationParam("float", field_type=float, required=True),
        ValidationParam("str", field_type=str, required=True),
        ValidationParam("bool", field_type=bool, required=True),
    ]
    validate_payload(mock_app, specs)


@pytest.mark.parametrize(
    "test_input",
    [
        None,
        {"int": "1", "float": 123.45, "str": "hello world", "bool": True},
    ],
)
def test_basic_types_invalid(test_input):
    mock_request = MagicMock(spec_set=Request)
    mock_log = MagicMock()
    mock_app = MagicMock(Chalice)
    mock_app.current_request = mock_request
    mock_app.log = mock_log

    # valid, required and present
    mock_request.json_body = test_input
    specs = [
        ValidationParam("int", field_type=int, required=True),
        ValidationParam("float", field_type=float, required=True),
        ValidationParam("str", field_type=str, required=True),
        ValidationParam("bool", field_type=bool, required=True),
    ]
    with pytest.raises(BadRequestError):
        validate_payload(mock_app, specs)


def test_missing_field():
    mock_request = MagicMock(spec_set=Request)
    mock_log = MagicMock()
    mock_app = MagicMock(Chalice)
    mock_app.current_request = mock_request
    mock_app.log = mock_log

    mock_request.json_body = {"int": 1, "float": 123.45, "bool": "False"}
    specs = [
        ValidationParam("int", field_type=int, required=True),
        ValidationParam("float", field_type=float, required=True),
        ValidationParam("str", field_type=str, required=True),
        ValidationParam("bool", field_type=bool, required=False),
    ]
    with pytest.raises(BadRequestError):
        validate_payload(mock_app, specs)


@pytest.mark.parametrize(
    "test_input",
    [
        None,
        {
            "int": 1,
            "float": "123.45",
            "str": "hello world",
            "bool": True,
            "date": "2022-01-07",
        },
        {
            "int": 1,
            "float": 123.45,
            "str": 6,
            "bool": True,
            "date": "2022-01-07",
        },
        {
            "int": 1,
            "float": 123.45,
            "str": "hello world",
            "bool": "True",
            "date": "2022-01-07",
        },
        {
            "int": 1,
            "float": 123.45,
            "str": "hello world",
            "bool": True,
            "date": "foo",
        },
    ],
)
def test_query_param_validation(test_input):
    mock_request = MagicMock()
    mock_log = MagicMock()
    mock_app = MagicMock(Chalice)
    mock_app.current_request = mock_request
    mock_app.log = mock_log

    mock_request.query_params = test_input
    specs = [
        ValidationParam("int", field_type=int, required=True),
        ValidationParam("float", field_type=float, required=True),
        ValidationParam("str", field_type=str, required=True),
        ValidationParam("bool", field_type=bool, required=True),
        ValidationParam("date", field_type=date, required=True),
    ]
    with pytest.raises(BadRequestError):
        validate_query_params(mock_app, specs)


def test_ints_with_limits():
    mock_request = MagicMock(spec_set=Request)
    mock_log = MagicMock()
    mock_app = MagicMock(Chalice)
    mock_app.current_request = mock_request
    mock_app.log = mock_log

    # valid, required and present
    mock_request.json_body = {"int": 1}

    spec = ValidationParam("int", field_type=int, required=True, min=0)
    mock_request.json_body = {"int": 1}
    validate_payload(mock_app, [spec])
    mock_request.json_body = {"int": 0}
    validate_payload(mock_app, [spec])

    mock_request.json_body = {}
    with pytest.raises(BadRequestError):
        validate_payload(mock_app, [spec])

    spec = ValidationParam("int", field_type=int, required=True, min=1, max=3)
    mock_request.json_body = {"int": 1}
    validate_payload(mock_app, [spec])
    mock_request.json_body = {"int": 3}
    validate_payload(mock_app, [spec])

    mock_request.json_body = {"int": 0}
    with pytest.raises(BadRequestError):
        validate_payload(mock_app, [spec])

    mock_request.json_body = {"int": 2.9}
    with pytest.raises(BadRequestError):
        validate_payload(mock_app, [spec])


def test_query_param_optional_with_none():
    mock_request = MagicMock()
    mock_log = MagicMock()
    mock_app = MagicMock(Chalice)
    mock_app.current_request = mock_request
    mock_app.log = mock_log

    # valid, required and present
    mock_request.query_params = None
    specs = [
        ValidationParam("int", field_type=int, required=False),
    ]
    validate_query_params(mock_app, specs)
