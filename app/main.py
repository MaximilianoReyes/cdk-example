from fastapi import FastAPI

from routes import inventory, user

from utils.exceptions import (
    DuplicateRecord,
    NotFoundRecord,
    Unauthorized,
    Forbidden,
    duplicate_record_exception_handler,
    not_found_exception_handler,
    unauthorized_exception_handler,
    forbidden_exception_handler,
)

app = FastAPI()

app.include_router(inventory.router)
app.include_router(user.router)

app.add_exception_handler(DuplicateRecord, duplicate_record_exception_handler)
app.add_exception_handler(NotFoundRecord, not_found_exception_handler)
app.add_exception_handler(Unauthorized, unauthorized_exception_handler)
app.add_exception_handler(Forbidden, forbidden_exception_handler)

@app.get("/healthcheck") #Prefijo
async def healthcheck():
    return {
        "healthcheck": "Noemi"
    } 