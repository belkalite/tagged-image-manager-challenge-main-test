import json
from typing import Tuple

import pytest
from chalice.test import Client
from sqlalchemy.orm.session import Session

from app import app
from chalicelib.models import Tag


@pytest.fixture
def sample_tag(db_session: Session) -> Tuple[int, str]:
    tag = Tag(name="sample tag")
    db_session.add(tag)
    db_session.commit()
    return tag.id, tag.name


def test_tags(sample_tag):
    with Client(app) as client:
        tag_id, tag_name = sample_tag
        response = client.http.get("/v1/tags").json_body
        actual_tag = [r for r in response["results"] if r["id"] == tag_id][
            0
        ]
        assert actual_tag == {"id": tag_id, "name": tag_name}


def test_create_tag(db_session):
    with Client(app) as client:
        tag_name = "tag 1"
        response = client.http.post(
            "/v1/tags",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"name": tag_name}),
        )
        assert response.json_body["name"] == tag_name

        # tag with same name only created once
        response = client.http.post(
            "/v1/tags",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"name": tag_name}),
        )
        assert response.json_body["name"] == tag_name

        assert db_session.query(Tag).where(Tag.name == tag_name).count() == 1


def test_tag(sample_tag):
    tag_id, tag_name = sample_tag
    with Client(app) as client:
        # exists
        response = client.http.get(f"/v1/tags/{tag_id}").json_body
        # assert response.json_body is not None
        assert response["id"] == tag_id
        assert response["name"] == tag_name

        # not exist
        response = client.http.get(f"/v1/tags/0")
        assert response.json_body["Code"] == "NotFoundError"
        assert response.status_code == 404


def test_tag_update(db_session, sample_tag):
    tag_id, tag_name = sample_tag
    new_tag_name = "sample tag x"
    with Client(app) as client:
        response = client.http.put(
            f"/v1/tags/{tag_id}",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"name": new_tag_name}),
        )
        assert response.json_body["name"] == new_tag_name


def test_tag_delete():
    with Client(app) as client:
        tag_id = 1
        response = client.http.delete(f"/v1/tags/{tag_id}").json_body
        assert response == {}
        response = client.http.get(f"/v1/tags/{tag_id}")
        assert response.status_code == 404


@pytest.mark.xfail(reason="get images for tag is not implemented yet")
def test_tag_images():
    # not implemented yet
    with Client(app) as client:
        response = client.http.get("/v1/tags/1/images")
        assert response.json_body == {}
