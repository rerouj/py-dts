from .fixture import client, store_settings_fixture

def test_document_get_document_returns_200_with_valid_query(client, store_settings):
    response = client.get("/api/dts/v1/document?resource=st-augustin-confessions&media_type=text/xml")
    assert response.status_code == 200

def test_document_get_document_404_invalid_query(client, store_settings):
    response = client.get("/api/dts/v1/document?resource=foo_text&media_type=text/xml")
    assert response.status_code == 404