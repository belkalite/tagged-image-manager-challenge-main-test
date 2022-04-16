import json
from random import sample

import pytest
from chalice.test import Client
from sqlalchemy.orm.session import Session

from app import app
from chalicelib.models import Tag
from tests.helpers import dict_assert


@pytest.fixture
def sample_tag(db_session: Session) -> int:
    tag = Tag(name="sample tag")
    db_session.add(tag)
    db_session.commit()
    return tag.id


def test_tags(sample_tag):
    with Client(app) as client:
        response = client.http.get("/v1/tags").json_body
        actual_tag = [r for r in response["results"] if r["id"] == sample_tag][
            0
        ]
        assert actual_tag == {"id": sample_tag, "name": "sample tag"}


def test_create_tag(db_session):
    with Client(app) as client:
        response = client.http.post(
            "/v1/tags",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"name": "tag 1"}),
        )
        assert response.json_body["name"] == "tag 1"

        # tag with same name only created once
        response = client.http.post(
            "/v1/tags",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"name": "tag 1"}),
        )
        assert response.json_body["name"] == "tag 1"

        assert db_session.query(Tag).where(Tag.name == "tag 1").count() == 1


def test_tag(sample_tag):
    with Client(app) as client:
        # exists
        response = client.http.get(f"/v1/tags/{sample_tag}")
        assert response.json_body is not None

        # not exist
        response = client.http.get(f"/v1/tags/0")
        assert response.json_body is not None


def test_tag_update(db_session, sample_tag):
    with Client(app) as client:
        response = client.http.put(
            f"/v1/tags/{sample_tag}",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"name": "sample tag x"}),
        )
        assert response.json_body["name"] == "sample tag x"


def test_tag_delete():
    with Client(app) as client:
        client.http.delete("/v1/tags/1")


@pytest.mark.xfail()
def test_tag_images():
    # not implemented yet
    with Client(app) as client:
        response = client.http.get("/v1/tags/1/images")
        assert response.json_body == {}
