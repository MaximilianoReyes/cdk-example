from bson import ObjectId
from typing import Annotated  
from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi.responses import JSONResponse

from models.inventory import CreateInventory, GetInventory
from utils.database import get_db
from utils.validate_token import validate_token

router = APIRouter(
    prefix="/inventory",
    tags=[
        "Inventory"
    ],
)

@router.get("", dependencies=[Depends(validate_token)])
async def list_inventory(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    
        inventory_list = [inventory async for inventory in database.inventory.find({})]
    
        return JSONResponse(
            content=jsonable_encoder(inventory_list),
            status_code=200
        )

@router.post("", dependencies=[Depends(validate_token)]) #Aqui estaria el prefijo pero se puso antes
async def create_inventory(
    create_inventory: CreateInventory, 
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)]): #Para inyectar dependencias
    
    inserted_id = await database.inventory.insert_one(
        {
            "_id": str(ObjectId()),
            "name": create_inventory.name,
            "price": create_inventory.price,
            "category": create_inventory.category,
        }
    )
    
    return {"created_inventory": inserted_id.inserted_id}  