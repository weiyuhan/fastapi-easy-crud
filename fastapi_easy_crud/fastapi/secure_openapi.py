from typing import List

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.security.base import SecurityBase


def add_secure_setting(app: FastAPI, security_list: List[SecurityBase]) -> None:
    def decorate_openapi():
        openapi_schema = app.openapi()
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        if "securitySchemes" not in openapi_schema["components"]:
            openapi_schema["components"]["securitySchemes"] = {}
        if "security" not in openapi_schema:
            openapi_schema["security"] = []
        for scheme in security_list:
            key = scheme.scheme_name
            value = scheme.model
            openapi_schema["components"]["securitySchemes"][key] = jsonable_encoder(
                value, by_alias=True, exclude_none=True
            )
            openapi_schema["security"].append({key: []})
        return openapi_schema

    app.openapi_schema = decorate_openapi()
