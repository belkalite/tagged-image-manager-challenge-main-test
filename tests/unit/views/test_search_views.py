import pytest

from app import app
from chalice.test import Client
from tests.helpers import dict_assert


@pytest.mark.xfail(reason="search views are not implemented yet")
def test_search(snapshot):
    with Client(app) as client:
        response = client.http.get("/v1/search/images")
        dict_assert(response.json_body, snapshot)
