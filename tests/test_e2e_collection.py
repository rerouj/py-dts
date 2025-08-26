from .fixture import client, store_settings_fixture

def test_collection_get_endpoint_returns_200_with_valid_query(client, store_settings):
    response = client.get("/api/dts/v1/collection?id=1-1")
    assert response.status_code == 200

def test_collection_get_endpoint_returns_404_for_non_existent_resource(client, store_settings):
    response = client.get("/api/dts/v1/collection?id=non-existent-document")
    assert response.status_code == 404

def test_collection_get_endpoint_returns_200_default(client, store_settings):
    response = client.get("/api/dts/v1/collection")
    assert response.status_code == 200

def test_collection_bad_params_422(client, store_settings):
    """
    Test the collection endpoint with bad parameters
    """
    response = client.get("/api/dts/v1/collection?page=")
    assert response.status_code == 422
    # test out of range
    response = client.get("/api/dts/v1/collection?page=-1")
    assert response.status_code == 422

    response = client.get("/api/dts/v1/collection?page=10000001")
    assert response.status_code == 422

    response = client.get("/api/dts/v1/collection?limit=-1")
    assert response.status_code == 422

    response = client.get("/api/dts/v1/collection?limit=10000000")
    assert response.status_code == 422

    response = client.get("/api/dts/v1/collection?offset=-1")
    assert response.status_code == 422

    response = client.get("/api/dts/v1/collection?offset=10000000")
    assert response.status_code == 422

    response = client.get("/api/dts/v1/collection?page=-1")
    assert response.status_code == 422
    assert response.json()['error']['details'][0]['message'] == "Value error, page is out of range"

    # test invalid parent parameter
    response = client.get("/api/dts/v1/collection?nav=foo")
    assert response.status_code == 422
    assert response.json()['error']['details'][0]['message'] == "Input should be 'parents' or 'children'"

def test_collection_get_returned_representation(client, store_settings):
    """
    Test the collection endpoint with valid parameters
    """
    response = client.get("/api/dts/v1/collection?id=1")

    expected_properties = [
        '@context',
        '@id',
        '@type',
        'collection',
        'dtsVersion',
        'title',
        'totalParents',
        'totalChildren',
        'description',
        'member',
        'view'
    ]
    response_fields = list(response.json().keys())
    assert response_fields == expected_properties