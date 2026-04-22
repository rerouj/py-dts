from fastapi import APIRouter, Response, HTTPException
from lxml import etree
from starlette.responses import HTMLResponse, JSONResponse

from dts_api.deps.selectors import service_selector
from dts_api.model.ParameterModel import document_params

router = APIRouter()

@router.get("/", description="Document Root endpoint")
def get(query: document_params, service: service_selector):
    doc = service.get(query)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    if query.media_type == 'text/xml':
        return Response(content=etree.tostring(doc, encoding='UTF-8', pretty_print=True, xml_declaration=True), media_type="application/xml")
    if query.media_type == 'text/html':
        return HTMLResponse(str(doc))
    if query.media_type == 'application/json':
        return JSONResponse(content=doc)

@router.post("/", description="Document Post endpoint")
def post():
    return {"value": "ok"}

@router.patch("/", description="Document Patch endpoint")
def patch():
    return {"value": "ok"}

@router.delete("/", description="Document Delete endpoint")
def delete():
    return {"value": "ok"}