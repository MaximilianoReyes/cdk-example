import secrets

from bson import ObjectId
from typing import Annotated  
from fastapi import Depends, APIRouter
from motor.motor_asyncio import AsyncIOMotorDatabase
from utils.exceptions import DuplicateRecord

from models.user import CreateUser
from utils.database import get_db
from utils.exceptions import NotFoundRecord
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

@router.post("") #Aqui estaria el prefijo pero se puso antes
async def create_inventory(
    create_user: CreateUser, 
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)]): #Para inyectar dependencias
    
    user_exists = await database.users.find_one({
        "email": create_user.email
    })

    if user_exists:
        raise DuplicateRecord(f"User {create_user.email} already exists")
    
    inserted_id = await database.users.insert_one(
        {
            "_id": str(ObjectId()),
            "email": create_user.email,
            "token": secrets.token_hex(12),
        }
    )
    
    return {"created_user": inserted_id.inserted_id}

@router.get("")
async def get_user(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    user_id: str,
):
    user = await database.users.find_one(
        {
            "_id": user_id,
        }
    )

    return user

@router.delete("")
async def delete_inventory(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)], 
    user_id: str,    
):
    
    # Encontramos primero el item para guardar la id
    User = await database.users.find_one({"_id": user_id})
    
    # Hacemos una validacion para saber si existe
    if not User:
        raise NotFoundRecord(f"User with this id: {user_id} not found")
        
    # Eliminar el user
    await database.users.delete_one({"_id": user_id})
        
    return JSONResponse(
            content={"message": f"User '{User['_id']}' deleted successfully"},
            status_code=200
        ) 
    
@router.patch("")
async def update_inventory(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)], 
    user_id: str, 
    update_data: CreateUser,
):  
    # Encontramos primero el user para hacer la validacion 
    User = await database.users.find_one({"_id": user_id})
    
    
    # Hacemos una validacion para saber si existe
    if not User:
        raise NotFoundRecord(f"User with this id: {user_id} not found")
    
    # Actualizamos el user
    await database.users.update_one(
        {"_id": user_id},
        {"$set": update_data.dict()}
    )

    return JSONResponse(
            content={"message": f"Item '{user_id}' update successfully"},
            status_code=200
        )   