import base64
from pathlib import Path
from random import randint, sample
from typing import List

import requests

count = 300

all_tags = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "eta",
    "theta",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "xi",
    "omikron",
    "pi",
    "rho",
    "sigma",
    "tau",
    "upsilon",
    "phi",
    "chi",
    "psi",
    "omega",
]

image_data = Path("tests/samples/image-00000.dcm").read_bytes()
image_b64_bytes = base64.b64encode(image_data)
image_b64_str = image_b64_bytes.decode("utf-8")


def make_request(tags: List[str], number: int) -> int:
    # adds an image and returns is ID
    res = requests.post(
        "http://localhost:8000/v1/upload",
        json={
            "filename": f"image-{number}.dcm",
            "image_data": image_b64_str,
            "tags": tags,
        },
    )
    res.raise_for_status()
    return res.json()["id"]


for i in range(count):
    record_tags = sample(all_tags, randint(1, 6))
    new_id = make_request(record_tags, i)
    print(f"image record {new_id} created")
