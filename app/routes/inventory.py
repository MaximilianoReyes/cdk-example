from bson import ObjectId
from typing import Annotated  
from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi.responses import JSONResponse

from models.inventory import CreateInventory
from utils.database import get_db
from utils.validate_token import validate_token
from utils.exceptions import NotFoundRecord

router = APIRouter(
    prefix="/inventory",
    tags=[
        "Inventory"
    ],
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

@router.get("", dependencies=[Depends(validate_token)])
async def list_inventory(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    
        inventory_list = [inventory async for inventory in database.inventory.find({})]
    
        return JSONResponse(
            content=jsonable_encoder(inventory_list),
            status_code=200
        )

@router.delete("")
async def delete_inventory(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)], 
    inventory_id: str,    
):
    
    # Encontramos primero el item para guardar la id
    inventory = await database.inventory.find_one({"_id": inventory_id})
    
    # Hacemos una validacion para saber si existe
    if not inventory:
        raise NotFoundRecord(f"Item with this id: {inventory_id} not found")
        
    # Eliminar el item
    await database.inventory.delete_one({"_id": inventory_id})
        
    return JSONResponse(
            content={"message": f"Item '{inventory['_id']}' deleted successfully"},
            status_code=200
        )    
    
@router.patch("")
async def update_inventory(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)], 
    inventory_id: str, 
    update_data: CreateInventory,
):  
    # Encontramos primero el item para hacer la validacion 
    inventory = await database.inventory.find_one({"_id": inventory_id})
    
    
    # Hacemos una validacion para saber si existe
    if not inventory:
        raise NotFoundRecord(f"Item with this id: {inventory_id} not found")
    
    # Actualizamos el item
    await database.inventory.update_one(
        {"_id": inventory_id},
        {"$set": update_data.dict()}
    )

    return JSONResponse(
            content={"message": f"Item '{inventory_id}' update successfully"},
            status_code=200
        )   
    