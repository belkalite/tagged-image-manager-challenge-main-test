import base64
import json
import os
from pathlib import Path

import boto3
import pytest
from chalice.test import Client
from freezegun import freeze_time
from mypy_boto3_s3.service_resource import Bucket
from sqlalchemy.orm.session import Session

from app import app
from chalicelib.models import Image
from tests.helpers import dict_assert


@pytest.fixture
def bucket(mocker) -> Bucket:
    s3 = boto3.resource(
        "s3", endpoint_url=os.environ["S3_ENDPOINT"], region_name="us-east-1"
    )
    bucket_name = "the-bucket"
    mocker.patch(
        "chalicelib.models.Image.BUCKET_NAME",
        bucket_name,
    )
    return s3.create_bucket(Bucket=bucket_name)


@freeze_time("2021-11-03 21:00:00")
def test_upload(bucket: Bucket, db_session: Session, snapshot):
    image_data = Path("tests/samples/image-00000.dcm").read_bytes()
    image_b64_bytes = base64.b64encode(image_data)
    image_b64_str = image_b64_bytes.decode("utf-8")

    with Client(app) as client:
        response = client.http.post(
            "/v1/upload",
            headers={"Content-Type": "application/json"},
            body=json.dumps(
                {
                    "filename": "image-00000.dcm",
                    "image_data": image_b64_str,
                    "tags": ["foo", "bar"],
                }
            ),
        ).json_body
        actual_tags = [t["name"] for t in response["tags"]]
        assert "bar" in actual_tags
        assert "foo" in actual_tags

        del response["tags"]
        del response["url"]
        dict_assert(response, snapshot)

        image_id = response["id"]
        image: Image = db_session.query(Image).filter_by(id=image_id).first()
        assert image.upload_timestamp is not None
        assert len(image.tags) > 0

    bucket_objects = [x for x in bucket.objects.all()]
    assert len(bucket_objects) >= 1
    assert bucket_objects[0].key.startswith("2021/11/03/")
    assert bucket_objects[0].key.endswith("/image-00000.dcm")
    assert bucket_objects[0].get()["Body"].read() == image_data
