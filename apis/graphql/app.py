"""Nexora GraphQL API (api02.nexora.test)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Nexora GraphQL API")
DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))


class GraphQLRequest(BaseModel):
    query: str
    variables: dict | None = None


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "api-graphql"})


@app.post("/graphql")
def graphql_endpoint(req: GraphQLRequest) -> dict:
    q = req.query.strip()
    if "__schema" in q:
        return {
            "data": {
                "__schema": {
                    "types": [
                        {"name": "Query", "fields": ["products", "departments"]},
                        {"name": "Product", "fields": ["sku", "name", "price"]},
                    ]
                }
            }
        }
    data = json.loads(DATA_PATH.read_text(encoding="utf-8")) if DATA_PATH.exists() else {"products": [], "departments": []}
    result: dict = {}
    if "products" in q:
        result["products"] = data.get("products", [])
    if "departments" in q:
        result["departments"] = data.get("departments", [])
    return {"data": result}
