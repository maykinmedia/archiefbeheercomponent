import os
import random
from typing import Any, Dict, List

from django.utils import timezone

import yaml
from faker import Faker
from requests_mock import Mocker

fake = Faker()
MOCK_FILES_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "schemas",
)

_cache = {}


def read_schema(service: str):
    if service not in _cache:
        file_name = f"{service}.yaml"
        file = os.path.join(MOCK_FILES_DIR, file_name)
        with open(file, "rb") as api_spec:
            _cache[service] = api_spec.read()

    return _cache[service]


def mock_service_oas_get(m: Mocker, url: str, service: str, oas_url: str = "") -> None:
    if not oas_url:
        oas_url = f"{url}schema/openapi.yaml?v=3"
    content = read_schema(service)
    m.get(oas_url, content=content)


def generate_oas_component(
    service: str,
    component: str,
    **properties,
) -> Dict[str, Any]:
    """
    Generate an object conforming to the OAS schema definition.

    Any extra kwargs passed in are used as explicit values for properties.
    """
    schema = yaml.safe_load(read_schema(service))

    definition = schema["components"]
    for bit in component.split("/"):
        definition = definition[bit]

    assert (
        definition["type"] == "object"
    ), "Types other than object are not supported (yet)"

    return generate_object(schema, definition, **properties)


def generate_object(schema: dict, definition: dict, **properties):
    obj = properties.copy()

    if "discriminator" in definition:
        # Not implemented yet...
        return {}

    for prop, prop_def in definition["properties"].items():
        if prop in obj:
            continue
        obj[prop] = generate_prop(schema, prop_def)
    return obj


def generate_prop(schema: dict, prop_definition: dict) -> Any:
    if "$ref" in prop_definition:
        ref_bits = prop_definition["$ref"].replace("#/", "", 1).split("/")
        prop_definition = schema
        for bit in ref_bits:
            prop_definition = prop_definition[bit]

    prop_type = prop_definition["type"]

    if prop_definition.get("nullable"):
        return None

    enum = prop_definition.get("enum")
    if enum:
        return random.choice(enum)

    if prop_type == "string":
        fmt = prop_definition.get("format")
        if fmt == "uri":
            return fake.url(schemes=["https"])

        elif fmt == "duration":
            return "P3W"

        elif fmt == "date":
            return fake.date()

        elif fmt == "date-time":
            return fake.date_time(tzinfo=timezone.utc).isoformat()

        elif fmt is None:
            return fake.pystr(
                min_chars=prop_definition.get("minLength"),
                max_chars=prop_definition.get("maxLength", 20),
            )

    elif prop_type == "boolean":
        return fake.pybool()

    elif prop_type == "array":
        item = generate_prop(schema, prop_definition["items"])
        return [item]

    elif prop_type == "object":
        return generate_object(schema, prop_definition)


def paginated_response(results: List[dict]) -> Dict[str, Any]:
    body = {
        "count": len(results),
        "previous": None,
        "next": None,
        "results": results,
    }
    return body
