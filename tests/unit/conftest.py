import os
from pathlib import Path
from typing import Tuple

import pytest
import boto3
from sqlalchemy import create_engine
from mypy_boto3_s3.service_resource import Bucket
from sqlalchemy.orm.session import Session, sessionmaker

from chalicelib.models import Base, Tag


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(autouse=True, scope="session")
def db_engine():
    tmp_db = Path("test.sqlite")

    if tmp_db.exists():
        tmp_db.unlink()

    db_url = f"sqlite+pysqlite:///{tmp_db.name}"
    os.environ["DB_URL"] = db_url
    db_engine = create_engine(db_url, echo=False, future=True)
    Base.metadata.create_all(db_engine)
    return db_engine


@pytest.fixture
def db_session(db_engine) -> Session:
    Session = sessionmaker(bind=db_engine)
    session = Session()

    return session


@pytest.fixture
def sample_tag(db_session: Session) -> Tuple[int, str]:
    tag = Tag(name="sample tag")
    db_session.add(tag)
    db_session.commit()
    return tag.id, tag.name


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