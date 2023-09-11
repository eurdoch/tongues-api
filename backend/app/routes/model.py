from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Depends,
)

from app.utils.auth import is_authorized
from app.models.completion import Model

router = APIRouter(
    prefix="/api/v0",
    dependencies=[Depends(is_authorized)],
)

@router.get(
    "/models"
)
async def get_model(
    section: str, 
    language: str,
) -> Model:
    model = await Model.find_one(Model.section == section, Model.language == language)
    if model is None:
        raise HTTPException(404)
    return model

# TODO Add admin auth
@router.post(
    "/models"
)
async def add_model(
    model: Model,
) -> Model:
    old_model = await Model.find_one(Model.section == model.section, Model.language == model.language)
    if old_model is not None:
        raise HTTPException(401)
    await model.create()
    return model

# TODO Require admin auth 
@router.put(
    "/models"
)
async def update_model(
    model: Model,
) -> Model:
    old_model = await Model.find_one(Model.section == model.section)
    old_model.name = model.name
    await old_model.save()
    return old_model

# TODO Require admin auth
@router.delete(
    "/models/{section}",
)
async def delete_model(section: str):
    model_to_delete = await Model.find_one(Model.section == section)
    await model_to_delete.delete()
