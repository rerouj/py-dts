from dts_api.model.NavigationModel import NavigationModel, CitableUnit
from .fixture import client, store_settings_fixture, LocalSettings

from .fixture import client, store_settings_fixture

def test_navigation_get_endpoint_returns_200_with_valid_query(client, store_settings):
    response = client.get("/api/dts/v1/navigation?resource=short-document")
    assert response.status_code == 200
    response = client.get("/api/dts/v1/navigation?resource=short-document&ref=Jean")
    assert response.status_code == 200
    response = client.get("/api/dts/v1/navigation?resource=short-document&start=Jean 1:1&end=Jean 1:2")
    assert response.status_code == 200
    response = client.get("/api/dts/v1/navigation?resource=short-document&start=Jean 1:1&end=Jean 1:2")
    assert response.status_code == 200
    response = client.get("/api/dts/v1/navigation?resource=short-document&down=-1")
    assert response.status_code == 200

def test_navigation_get_content(client, store_settings: LocalSettings):
    """
    Test the navigation endpoint with valid parameters
    """
    response = client.get("/api/dts/v1/navigation?resource=short-document&ref=Jean&down=-1")
    assert response.status_code == 200
    content = response.json()
    assert content['@id'] == "short-document"
    assert content['resource'] is not None
    assert len(content['resource']) > 0
    assert content['member'] is not None
    assert len(content['member']) > 0

    nav_keys = list(NavigationModel().model_dump(exclude={"ref", "start", "end"}, by_alias=True).keys())

    response_fields = [k for k in list(content.keys()) if k not in ["ref", "start", "end"]]
    for k in response_fields:
        assert k in nav_keys, f"Key {k} not in NavigationModel"

    # test ref, start, end content
    assert content['ref']['parent'] is None # top level refs parent field should be set to null
    citable_unit_keys = list(CitableUnit(level=0, dublin_core=[]).model_dump().keys())
    response_fields = list(content['ref'].keys())
    assert citable_unit_keys == response_fields

    response = client.get("/api/dts/v1/navigation?resource=short-document&start=Jean 1:1&end=Jean 1:3&down=-1")
    content = response.json()
    response_fields = list(content['start'].keys())
    citable_unit_keys.pop() # remove optional fields ('dublinCore', 'extensions')
    assert citable_unit_keys == response_fields
    response_fields = list(content['end'].keys())
    assert citable_unit_keys == response_fields
