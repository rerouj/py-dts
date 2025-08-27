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

An example of such metadata file can be found in the `tests/dummy/local-storage-data/metadata.json` file.

When your database is ready, you have to configure the API to point to your data storage.
This can be done by setting the `STORAGE` environment variable (.env).

You also have to provide the base path to your storage and the path to your metadata file by setting the `METADATA_PATH` environment variable (.env).

## Usage

If your server is running locally, it should be available at `http://localhost:8000/docs`.

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

- add JsonDesigner class to design a json representation of a Document.
- add a Dockerfile to build and run a containerized version of the api.
- allow non dublin core metadata to be extracted from an XML document and inserted inside the 'extension' field of a Navigation representation
- add profileDesc extractor feature, allow dc metadata from xml file at the main level, convert and insert those data inside a Collection representation
- same thing for non dc metadata, allow them to be extracted from an XML document and inserted inside the 'extension' field of a Collection representation
- The metadata must include a field that indicates the status regarding the permanence of the served object (ARK). If the object is deleted, the entry indicates, for example, "deleted" or "archived."