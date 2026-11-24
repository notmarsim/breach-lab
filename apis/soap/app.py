"""Nexora Legacy SOAP/XML Service."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(title="Nexora SOAP Service")

WSDL_DOC = """<?xml version="1.0" encoding="UTF-8"?>
<definitions name="NexoraInventoryService" targetNamespace="http://nexora.test/soap"
  xmlns="http://schemas.xmlsoap.org/wsdl/">
  <message name="GetServiceStatusRequest"/>
  <message name="GetServiceStatusResponse"/>
</definitions>"""


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "api-soap"})


@app.get("/soap")
def get_wsdl() -> Response:
    return Response(content=WSDL_DOC, media_type="application/xml")


@app.post("/soap")
async def soap_call(request: Request) -> Response:
    raw = await request.body()
    try:
        ET.fromstring(raw.decode("utf-8"))
    except ET.ParseError:
        return Response(content="<Fault>Invalid XML</Fault>", media_type="application/xml", status_code=400)
    envelope = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
        "<soap:Body><GetServiceStatusResponse><Status>OPERATIONAL</Status></GetServiceStatusResponse></soap:Body>"
        "</soap:Envelope>"
    )
    return Response(content=envelope, media_type="application/xml")
