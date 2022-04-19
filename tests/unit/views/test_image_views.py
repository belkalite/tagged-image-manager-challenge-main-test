import json

import pytest
from freezegun import freeze_time
from sqlalchemy.orm.session import Session
from chalicelib.models import Image
from tests.helpers import dict_assert, http_api
from tests.helpers.build_image import build_image


@pytest.mark.smoke
@freeze_time("2021-11-03 21:00:00")
def test_images(db_session: Session, snapshot):
    max_id = 200
    for i in range(1, max_id):
        build_image(db_session=db_session, id=i)
    response = http_api.get("/images").json_body

    assert response["meta"] is not None, "No meta data in response"
    dict_assert(response, snapshot, "page-1")  # TODO update snapshots in right orders

    # get second page
    response = http_api.get("/images?page=1").json_body
    dict_assert(response, snapshot, "page-2")
    assert response["meta"] is not None, "No meta data in response"
    image = db_session.query(Image).all()
    assert len(image) == max_id-1, "Images count is not equal to added"


@freeze_time("2021-11-03 21:00:00")
def test_new_images_return_first(db_session: Session):
    response = http_api.get("/images").json_body
    first_image = response["results"][0]
    assert first_image["id"] == 199, "New added image is not on the top of the list"


@pytest.mark.smoke
@freeze_time("2021-11-03 21:00:00")
def test_image_post(db_session: Session):
    response = http_api.post(
        "/images",
        headers={"Content-Type": "application/json"},
        body=json.dumps(
            {"filename": "test.dcm", "size": 1234, "tags": ["bar", "baz"]}
        ),
    ).json_body
    image_id = response["id"]

    assert isinstance(response["id"], int), "Data type of the 'id' field is not 'int'"
    assert response["upload_url"].startswith("http"), "Upload url has invalid format"
    response = http_api.get(f"/images/{image_id}").json_body
    assert response["filename"] == "test.dcm", "Created image has wrong 'filename'"
    assert response["size"] == 1234, "Created image has wrong 'size'"
    assert len(response["tags"]) > 0, "Created image has wrong tags count"


@pytest.mark.smoke
@freeze_time("2021-11-03 21:00:00")
def test_image_get(db_session, snapshot):
    build_image(db_session=db_session)

    response = http_api.get("/images/1").json_body
    del response["url"]

    dict_assert(response, snapshot)


@freeze_time("2021-11-03 21:00:00")
def test_get_image_not_exists(db_session):
    http_api.get("/images/0", expected_code=404)


@pytest.mark.smoke
@freeze_time("2021-11-03 21:00:00")
def test_image_update(db_session, snapshot):
    image = build_image(db_session=db_session, tags=["foo"])

    response = http_api.put(
        f"/images/{image.id}",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"tags": ["foo", "bar", "baz"]}),
    ).json_body
    del response["url"]
    del response["filename"]
    dict_assert(response, snapshot)

    assert "foo" in [t.name for t in image.tags]


@pytest.mark.xfail(reason="delete image is not implemented yet")
def test_image_delete(db_session):
    image = build_image(db_session=db_session)
    id = image.id

    response = http_api.delete(f"/images/{id}", expected_code=204)
    assert response.json_body == {}, "Wrong response body"
    assert db_session.query(Image).filter_by(id=id).count() == 0, "Image was not deleted"
