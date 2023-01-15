import jsonschema

# The schema for the hello message
message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "hello message",
    "title": "Hello message",
    "description": "The schema for the hello message",
    "type": "object",
    "properties": {
        "type": {
            "description": "The type of the message",
            "type": "string",
            "enum": ["hello", "ciao"]
        }
    },
    "required": ["type"],
}

message = {
    "type": "hello",
    "some_other_key": "some_other_value"
}

try:
    jsonschema.validate(message, message_schema)
    print("The message is valid")
except jsonschema.exceptions.ValidationError as e:
    print(e)

message2 = {
    "type": "ciao bella",
    "some_other_key": "some_other_value"
}

try:
    jsonschema.validate(message2, message_schema)
    print("The message is valid")
except jsonschema.exceptions.ValidationError as e:
    print(e)