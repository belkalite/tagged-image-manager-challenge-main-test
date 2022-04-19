from typing import List, Optional

from sqlalchemy.orm.session import Session
from chalicelib.db import get_or_create
from chalicelib.models import Image, Tag


def build_image(
        db_session: Session,
        id: Optional[int] = None,
        created_by: str = "test-user",
        created_timestamp: int = 1635926694,
        size=256000,
        upload_timestamp: Optional[int] = 1635926694,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = ("foo", "bar", "baz"),
) -> Image:
    filename = f"sample-{id}.dcm"
    if prefix is None and upload_timestamp is not None:
        prefix = "archive/2021/11/03/19-06-{id}/"

    image = Image(
        id=id,
        filename=filename,
        created_by=created_by,
        created_timestamp=created_timestamp,
        size=size,
        upload_timestamp=upload_timestamp,
        prefix=prefix,
    )

    if tags is not None:
        for tag in tags:
            tag_rec: Tag = get_or_create(db_session, Tag, name=tag)
            image.tags.append(tag_rec)

    db_session.add(image)
    db_session.commit()
    return image
