from enum import Enum
from typing import Any, Dict, List, Optional, Union

from fastapi.routing import APIRoute


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        str_tags = [
            tag.value if isinstance(tag, Enum) else str(tag) for tag in route.tags
        ]
        prefix = "-".join(str_tags) if route.tags else ""
        return f"{prefix}-{route.name}"
    return route.name


def generate_default_servers(
    root_path: Optional[str] = None,
    servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
) -> Optional[List[Dict[str, Union[str, Any]]]]:
    servers = servers or []
    if root_path and root_path.rstrip("/"):
        servers.insert(
            0,
            {
                "url": root_path,
            },
        )
    return servers
