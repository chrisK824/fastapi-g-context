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
