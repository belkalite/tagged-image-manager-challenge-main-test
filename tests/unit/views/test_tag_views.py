import json
import pytest

from chalicelib.models import Tag
from tests.helpers import http_api


@pytest.mark.smoke
def test_tags(sample_tag):
    response = http_api.get("/tags").json_body
    tag_id, tag_name = sample_tag
    assert response["results"] != [], "Can not get all tags"
    actual_tag = [result for result in response["results"] if result["id"] == tag_id][0]
    assert actual_tag == {"id": tag_id, "name": tag_name}, "Can not get tag"


@pytest.mark.smoke
def test_create_tag(db_session):
    tag_name = "tag 1"
    response = http_api.post("/tags",
                             headers={"Content-Type": "application/json"},
                             body=json.dumps({"name": tag_name}),
                             )
    assert response.json_body["name"] == tag_name, "Wrong 'name' in response"

    # tag with same name only created once
    response = http_api.post("/tags",
                             headers={"Content-Type": "application/json"},
                             body=json.dumps({"name": tag_name}),
                             )
    assert response.json_body["name"] == tag_name, "Wrong 'name' in response"
    assert db_session.query(Tag).where(Tag.name == tag_name).count() == 1, "Tag with the same name was not created once"


@pytest.mark.smoke
def test_tag(sample_tag):
    tag_id, tag_name = sample_tag
    response = http_api.get(f"/tags/{tag_id}").json_body
    assert response["id"] == tag_id, "Wrong 'id' in response"
    assert response["name"] == tag_name, "Wrong 'name' in response"


def test_get_tag_not_exists():
    http_api.get(f"/tags/0", expected_code=404)


@pytest.mark.smoke
def test_tag_update(db_session, sample_tag):
    tag_id, tag_name = sample_tag
    new_tag_name = "sample tag x"
    response = http_api.put(
        f"/tags/{tag_id}",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"name": new_tag_name}),
    )
    assert response.json_body["name"] == new_tag_name, "Wrong 'name' in response"


def test_tag_delete():
    tag_id = 1
    response = http_api.delete(f"/tags/{tag_id}").json_body
    assert response == {}, "Wrong response body"
    http_api.get(f"/tags/{tag_id}", expected_code=404)


@pytest.mark.smoke
@pytest.mark.xfail(reason="get images for tag is not implemented yet")
def test_tag_images():
    # not implemented yet
    response = http_api.get("/tags/1/images")
    assert response.json_body == {}, "Wrong response body"
