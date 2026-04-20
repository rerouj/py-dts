# PY-DTS - a Python implementation of the DTS api

This project implements the DTS API specification in Python. It provides a RESTful web service to manage and serve text documents, collections, and their metadata.
It also includes tools to extract metadata from XML documents and convert them into the appropriate DTS representations.
The project is built using FastAPI for the web framework and Pydantic for data validation and serialization.

full API purpose and specification can be found here:

https://distributed-text-services.github.io/specifications/

actual DTS api implementation version is **1-alpha**.

## Features

- RESTful API for requesting documents and collections
- Metadata extraction from XML documents (Dublin Core)
- OpenAPI documentation for easy API exploration
- Unit tests to ensure code quality and reliability
- Modular design for easy extension and customization
- Asynchronous support for handling multiple requests efficiently
- CORS support for cross-origin requests
- Example data and scripts for testing and demonstration
- Error handling and validation for robust API interactions
- Support for multiple storage backends (local filesystem, GitHub, ExistDb)

## Installation

To run the api locally, clone the repository and install the required dependencies with Poetry:

```bash
git clone
cd py-dts
poetry install
```
then, if you have `uvicorn` installed, you can run:
```bash
uvicorn main:app --reload
```

FastAPI launcher can also be used if you have it installed:
```bash
fastapi dev main.py
```

deployment documentation can be found in the FastAPI documentation.

https://fastapi.tiangolo.com/deployment/manually/

## Configuration

To use the API, ensure that your documents are stored in the appropriate data storage.
PY-DTS supports local filesystem storage and GitHub storage backends.

Available storage backends can be extended by implementing a new Database class and a new FileStorage class.

PY-DTS does not impose a specific directory structure for your documents, but it is recommended to follow a consistent structure for easier management.
Nevertheless, PY-DTS needs a metadata file in JSON format to describe the collections and documents available in the storage.

The manifest.json can be served by a tier server or can be stored locally and served by the API itself.

An example of such metadata file can be found in the `tests/dummy/local-storage-data/metadata.json` file.

When your database is ready, you have to configure the API to point to your data storage.
This can be done by setting the `STORAGE` environment variable (.env). An example of such configuration can be found in the `.env.template` file.

You also have to provide the base path to your storage and the path to your metadata file by setting the `METADATA_PATH` environment variable (.env).

## Docker

PY-DTS can also be deployed using Docker with :

```bash
docker/podman run -p 8000:8000 --name pydts renatodiaz/py-dts:latest
```

Available tags are provided in the [DockerHub repository]("https://hub.docker.com/repository/docker/renatodiaz"). You can also build the image locally with the provided Dockerfile.

## Variables

The API can be configured with the following environment variables:

- `APP_NAME`: the name of the application, used in the API documentation.
- `APP_DESCRIPTION`: a short description of the application, used in the API documentation.
- `APP_AUTHOR_INFOS`: a dict containing the name and email of the author, used in the API documentation.
- `APP_URL`: a JSON string containing a list of URLs and their descriptions, used in the API documentation.
- `DTS_CONTEXT`: the URL of the DTS context to use for JSON-LD serialization, the default value is `https://distributed-text-services.github.io/specifications/context/1-alpha1.json`.
- `DTS_VERSION`: the version of the DTS specification to use, the default value is `1-alpha`.
- `ROOT_COLLECTION`: the root collection to use, the default value is `None`.
- `ALLOWED_ORIGINS`: a list of allowed origins for CORS settings, set to `*` to allow all origins, or specify a comma-separated list of allowed origins (e.g. `http://localhost:3000,http://example.com`).
- `STORAGE`: the storage backend to use, available options are `local` and `github`.
- `INDEXER`: the indexer to use, available options are `standard` (the default one) and `custom` (not implemented yet).
- `BASE_PATH`: the base path to the storage, not needed for github storage, but required for local storage.
- `METADATA_PATH`: the path to the metadata file, can be a local path or a URL, depending on the storage backend used.
- `TEI_NS`: the TEI namespace to use for XML parsing, the default value is `http://www.tei-c.org/ns/1.0`.


## Usage

If your server is running locally, it should be available at `http://localhost:8000/docs` or `http://localhost:8000/redoc`. The API contract is available at `http://localhost:8000/openapi.json`.

the root endpoint is `http://localhost:8000/api/dts/v1`. (url prefix can be modified in the `main.py` file.)

The API documentation can be found at `https://distributed-text-services.github.io/specifications/`, but we provide here a few basic examples in Curl.

### Example requests

- Get all collections infos:
  curl --request GET \
  --url http://127.0.0.1:8000/api/dts/v1/collection
- Get a document infos by ID:
  curl --request GET \
  --url 'http://127.0.0.1:8000/api/dts/v1/collection?id=short-document'
- Get available navigation references for a document:
  curl --request GET \
  --url 'http://127.0.0.1:8000/api/dts/v1/navigation?resource=short-document&ref=Jean&down=-1&limit=10'
- Get a document:
  curl --request GET \
  --url 'http://127.0.0.1:8000/api/dts/v1/document?resource=vat-gr-1190&media_type=text%2Fxml'
- Get an excerpt:
  curl --request GET \
  --url 'http://127.0.0.1:8000/api/dts/v1/document?resource=st-augustin-confessions&ref=1.1&media_type=text%2Fxml'
- Get an HTML version of a document (not available for excerpts):
curl --request GET \
  --url 'http://127.0.0.1:8000/api/dts/v1/document?resource=st-augustin-confessions&media_type=text%2Fhtml'

## caveat
### about the lines (<lb \/> tag)

The API currently support the ```<lb/>``` tag as a line tag, but, in order to work properly, there is two conditions:
- a citeStrucure with a ```use``` parameter set to ```@n``` will only map a ```lb``` with a provided ```n``` attribute.
- you should add a "ghost" ```<lb/>``` tag before the first line of the document, with a ```n``` attribute equal to ```first_line - 1``` or 0.
- citeStrucure with a ```use``` parameter set to ```position()``` will need an empy ```lb``` before the first line of the document.

**Generally, correctly formatted XML documents should be provided to the API, specially when the ```use``` parameter is set to a value that is not equal to ```position()```.**

An example is provided in the ```/tests/dummy/local-storage-data/database/mp/athous-iviron-450.xml``` file
for the moment the API does not bring information on document validation, but this will be added in the future.

## Dependencies

- poetry
- fastapi
- pydantic-settings
- pyfakefs
- lxml
- pytest

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any questions or issues, please open an issue on the GitHub repository or contact the maintainer at [renato.diaz@unil.ch]

Feel free to contribute to the project by submitting pull requests !

## Todos:

- add a parameter that limits the reading scope of a document. For instance ```scope: 107, 120``` would only read the main citation element between 107 and 120 of the document. the parameter is set into the manifest.json file.
- add JsonDesigner class to design a json representation of a Document.
- allow non dublin core metadata to be extracted from an XML document and inserted inside the 'extension' field of a Navigation representation
- add profileDesc extractor feature, allow dc metadata from xml file at the main level, convert and insert those data inside a Collection representation
- same thing for non dc metadata, allow them to be extracted from an XML document and inserted inside the 'extension' field of a Collection representation
- The metadata must include a field that indicates the status regarding the permanence of the served object (ARK). If the object is deleted, the entry indicates, for example, "deleted" or "archived."