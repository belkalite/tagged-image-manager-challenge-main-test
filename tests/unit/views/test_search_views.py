import pytest

from tests.helpers import dict_assert, http_api


@pytest.mark.xfail(reason="search views are not implemented yet")
def test_search(snapshot):
    response = http_api.get("/search/images")
    dict_assert(response.json_body, snapshot)
