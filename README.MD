# Tagged Image Manager Challenge

Read about [the API Design](<design-docs/API DESIGN.md>).

## Getting Started

Prerequisites:

- [direnv](https://direnv.net/)
- [pyenv](https://github.com/pyenv/pyenv)
- [Poetry](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions)

For running locally & testing:

- [docker](https://docs.docker.com/get-docker/) & [docker-compose](https://docs.docker.com/compose/install/)

Create your virtualenv, activate and install dependencies:

```shell
cp .envrc.example .envrc
direnv allow
pyenv install
poetry install
# ready fakes3 and postgres docker images
docker-compose pull
# create docker volume for database
docker volume create --name=dev-pgdata
```

Run the tests:

```shell
# for fake-s3
docker-compose up -d
make tests
```

## Run locally (fake-s3 & no cognito/auth required)

```shell
docker-compose up -d

# use direnv + .envrc to ensure local configuration is set
make run
```

In another shell (requires curl and [jq](https://stedolan.github.io/jq/)):

```shell
# if the database is new
make tables

# make a tag
curl "localhost:8000/v1/tags" \
  -XPOST \
  --header 'content-type: application/json' \
  --data-binary @- << EOF | jq
{
  "name": "some new tag"
}
EOF

# list tags
curl localhost:8000/v1/tags | jq

# upload an image
curl "localhost:8000/v1/upload" \
 -XPOST \
 --header 'content-type: application/json' \
 --data-binary @- <<EOF
{
  "filename": "image-0000.dcm",
  "image_data": "$(base64 -w0 samples/image-00000.dcm)",
  "tags": ["foo", "bar"]
}
EOF

# list images
curl "localhost:8000/v1/images" | jq
```

## Utility scripts

Add records to locally running instance:

```
$ make add-records
poetry run python -m scripts.add_records
image record 888 created
image record 889 created
image record 890 created
image record 891 created
...
```

To reset tables (and clear all data):

```
# shut down the server first!
$ make reset-tables
```

## Limitations

- s3 hooks do not run on fake_s3, so image urls will not be added at the end of an async image upload
- get images for tag (`/v1/tags/{tag_id}/images`) is not implemented
- delete image is not implemented
- search views (`v1/search/`) are not implemented
