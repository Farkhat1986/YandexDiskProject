FILES_LIST_SCHEMA = {
    "type": "object",
    "required": ["items", "limit", "offset", "path", "total"],
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "path"],
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string", "enum": ["file", "dir"]},
                    "path": {"type": "string"},
                    "created": {"type": ["string", "null"]},
                    "modified": {"type": ["string", "null"]},
                    "mime_type": {"type": ["string", "null"]},
                    "size": {"type": ["integer", "null"]},
                    "md5": {"type": ["string", "null"]},
                },
                "additionalProperties": False,
            },
        },
        "limit": {"type": "integer"},
        "offset": {"type": "integer"},
        "path": {"type": "string"},
        "total": {"type": "integer"},
    },
    "additionalProperties": False,
}
