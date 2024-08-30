# fastapi-g-context

`fastapi-g-context` is a Python module that provides a simple mechanism for managing global variables with context isolation in `FastAPI` applications. It is designed to ensure that each request operates within its own isolated context, preventing data leakage between requests.

While this behaviour can be achieved in other ways as well, this module tries to mimic the `flask`'s global `g` object, so that `flask` users find it easier to migrate their logic when moving to `FastAPI`.


## Features

- **Context Isolation**: Each request operates in a fresh context, ensuring that global variables do not interfere with each other.
- **Easy-to-Use** Interface: Get, set, and manage global variables with a simple and intuitive API, while resembling the usage of `flask`'s `g` object to make it easier for users that are switching to `FastAPI`.
- **Middleware Integration**: Integrates seamlessly with FastAPI as a pure ASGI lightweight middleware.

## Installation

To install `fastapi-g-context` simply use pip:

`pip install fastapi-g-context`


## Usage
To use `fastapi-g-context` in your FastAPI application, follow these simple steps:

- Install the package: Ensure you have `fastapi-g-context` installed. You can add it to your requirements.txt or install it directly.
- Import the necessary components from `fastapi_g_context`: 
    - `GlobalsMiddleware` 
    - `g` object (the global context manager) .
- Add the GlobalsMiddleware to your FastAPI application. This middleware ensures that each request operates with a fresh context for global variables.
- Set Global Variables: You can set and manipulate global variables using the g object. These variables are request-scoped and won't leak between requests.
- Most usual use case would be to use that `g` object to set dependencies for your app's handlers via the `FastAPI`'s  dependency injection system.

```python
from fastapi import FastAPI, Depends
from fastapi_g_context import GlobalsMiddleware, g

app = FastAPI()
app.add_middleware(GlobalsMiddleware)

async def set_globals() -> None:
    g.username = "JohnDoe"
    g.request_id = "123456"
    g.is_admin = True

@app.get("/", dependencies=[Depends(set_globals)])
async def info():
    return {"username": g.username, "request_id": g.request_id, "is_admin": g.is_admin}

```

## API reference

The global object `g`  provides a mechanism to manage global variables with context isolation. Below are the methods and attributes available in this class:

**`key in g`**  
_Check whether an attribute is present in the global context._

- **Parameters**: 
  - `key` (str): The name of the attribute to check.
- **Return Type**: `bool`

**`g.get(name, default=None)`**  
_Get an attribute by name, or return a default value if the attribute is not present. This works similarly to `dict.get()`._

- **Parameters**:
  - `name` (str): Name of the attribute to retrieve.
  - `default` (Any | None): Value to return if the attribute is not present (default is `None`).
- **Return Type**: `Any`

**`g.pop(name, default=None)`**  
_Get and remove an attribute by name. This works similarly to `dict.pop()`._

- **Parameters**:
  - `name` (str): Name of the attribute to pop.
  - `default` (Any | None): Value to return if the attribute is not present (default is `None`).
- **Return Type**: `Any`

**`g.keys()`**  
_Return an iterator over the attribute names in the global context._

- **Return Type**: `Iterator[str]`

**`g.values()`**  
_Return an iterator over the attribute values in the global context._

- **Return Type**: `Iterator[Any]`

**`g.items()`**  
_Return an iterator over the attribute name-value pairs in the global context._

- **Return Type**: `Iterator[tuple[str, Any]]`

**`g.to_dict()`**  
_Return all attributes and their current values as a dictionary._

- **Return Type**: `Dict[str, Any]`

**`g.clear()`**  
_Clear all attributes from the global context._

- **Return Type**: `None`

**`g.__getattr__(name)`**  
_Retrieve the value of an attribute by name. Raises an `AttributeError` if the attribute is not found._

- **Parameters**:
  - `name` (str): Name of the attribute to retrieve.
- **Return Type**: `Any`

**`g.__setattr__(name, value)`**  
_Set the value of an attribute by name. Creates the attribute if it does not already exist._

- **Parameters**:
  - `name` (str): Name of the attribute to set.
  - `value` (Any): Value to set for the attribute.
- **Return Type**: `None`


## Example

To demonstrate the capabilities of the fastapi_g_context module, here's an example FastAPI application.

```python
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi_g_context import GlobalsMiddleware, g
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(GlobalsMiddleware)


async def set_globals() -> None:
    g.username = "JohnDoe"
    g.request_id = "123456"
    g.is_admin = True
    g.to_pop = "dispensable"


@app.get("/", dependencies=[Depends(set_globals)])
async def info():
    # Iterate over globals like a dictionary
    for name, value in g.items():
        logging.info(f"Global variable '{name}' has value: {value}")

    # Check for attributes/variables existence in globals
    logging.info(f"'username' is present in globals: {'username' in g}")
    logging.info(f"'password' is present in globals: {'password' in g}")

    # Usage of .get() with a default value or not
    logging.info(f"'non_existing_with_default' is present in globals: {'non_existing_with_default' in g}")
    non_existing_get_with_default = g.get("non_existing_with_default", "non_existing_default")
    logging.info(f"'non_existing_with_default' key has value: {non_existing_get_with_default}")

    # Default value defaults to None if not provided
    logging.info(f"'non_existing_none' is present in globals: {'non_existing_none' in g}")
    non_existing_get = g.get("non_existing_none")
    logging.info(f"'non_existing_none' key has value: {non_existing_get}")

    # Usage of .pop() with a default value or not
    logging.info(f"'non_existing_with_default' is present in globals: {'non_existing_with_default' in g}")
    non_existing_pop_with_default = g.pop("non_existing_with_default", "non_existing_default")
    logging.info(f"'non_existing_with_default' key has value: {non_existing_pop_with_default}")

    # Default value defaults to None if not provided
    logging.info(f"'non_existing_none' is present in globals: {'non_existing_none' in g}")
    non_existing_pop = g.pop("non_existing_none")
    logging.info(f"'non_existing_none' key has value: {non_existing_pop}")

    # Accessing a non-set variable directly like an attribute will lead to an AttributeError
    try:
        logging.info(f"'not_existing' is present in globals: {'not_existing' in g}")
        logging.info(g.not_existing)
    except AttributeError as e:
        logging.exception(e)

    # Retrieve an already set variable as an attribute
    logging.info(f"'username' key has value: {g.username}")

    # Set a new variable
    logging.info(f"'new_key' is present in globals: {'new_key' in g}")
    g.new_key = "new_value"
    logging.info(f"'new_key' is present in globals: {'new_key' in g}")

    # Pop an existing variable
    logging.info(f"'to_pop' is present in globals: {'to_pop' in g}")
    key_to_pop = g.pop("to_pop")
    logging.info(f"'to_pop' key has value: {key_to_pop}")
    logging.info(f"'to_pop' is present in globals: {'to_pop' in g}")

    # List all global variable names
    globals_keys = list(g.keys())

    # List all global variable values
    globals_values = list(g.values())

    # Get all global variables as a dictionary
    global_dict = g.to_dict()

    return JSONResponse(
        content={
            "global_keys": globals_keys,
            "global_values": globals_values,
            "global_dict": global_dict
        }
    )
```

After running this example app with `uvicorn example:app --host 0.0.0.0 --port 8080 --reload ` and requesting the only endpoint that it serves:

- The logs that are printed out:

```text
INFO:root:Global variable 'username' has value: JohnDoe
INFO:root:Global variable 'request_id' has value: 123456
INFO:root:Global variable 'is_admin' has value: True
INFO:root:Global variable 'to_pop' has value: dispensable
INFO:root:'username' is present in globals: True
INFO:root:'password' is present in globals: False
INFO:root:'non_existing_with_default' is present in globals: False
INFO:root:'non_existing_with_default' key has value: non_existing_default
INFO:root:'non_existing_none' is present in globals: False
INFO:root:'non_existing_none' key has value: None
INFO:root:'non_existing_with_default' is present in globals: False
INFO:root:'non_existing_with_default' key has value: non_existing_default
INFO:root:'non_existing_none' is present in globals: False
INFO:root:'non_existing_none' key has value: None
INFO:root:'not_existing' is present in globals: False
ERROR:root:'not_existing' variable does not exist in globals, make sure to set it before trying to use it
Traceback (most recent call last):
  File "/path/to/example.py", line 53, in info
    logging.info(g.not_existing)
                 ^^^^^^^^^^^^^^
  File "/path/to/fastapi_g_context.py", line 41, in __getattr__
    raise AttributeError(
AttributeError: 'not_existing' variable does not exist in globals, make sure to set it before trying to use it
INFO:root:'username' key has value: JohnDoe
INFO:root:'new_key' is present in globals: False
INFO:root:'new_key' is present in globals: True
INFO:root:'to_pop' is present in globals: True
INFO:root:'to_pop' key has value: dispensable
INFO:root:'to_pop' is present in globals: False
```

- The response returned:
```json
{
    "global_keys": [
        "username",
        "request_id",
        "is_admin",
        "new_key"
    ],
    "global_values": [
        "JohnDoe",
        "123456",
        true,
        "new_value"
    ],
    "global_dict": {
        "username": "JohnDoe",
        "request_id": "123456",
        "is_admin": true,
        "new_key": "new_value"
    }
}

```