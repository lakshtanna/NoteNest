from fastapi import APIRouter,Depends,HTTPException,status
from pydantic import BaseModel,Field
from typing import Optional,Annotated
from sqlalchemy.orm import Session
from Server import Session_Local
from Preview import CATEGORIES
from .Users import decode_token

CategoryRouter= APIRouter(prefix='/categories', 
                tags= ['CATEGORIES'])


def get_db():
    db= Session_Local()
    try:
        yield(db)
    finally:
        db.close()    


db_dependency= Annotated[Session, Depends(get_db)]
user_dependency= Annotated[dict, Depends(decode_token)]

class CategoryCreate(BaseModel):
    Name: str= Field(min_length= 3, examples= ["Programming"])
    Description: Optional[str]= Field(min_length=3, examples= ["Notes related to FastApi"])



@CategoryRouter.get('/',)
async def get_categories(db: db_dependency, user: user_dependency):
    return db.query(CATEGORIES).filter(CATEGORIES.User_id == user.get('id')).all()
     


@CategoryRouter.get('/{category_id}', status_code= status.HTTP_302_FOUND)
async def get_catgory(category_id: int, db: db_dependency, user: user_dependency):
    detail= db.query(CATEGORIES).filter(CATEGORIES.id == category_id).filter(CATEGORIES.User_id == user.get('id')).first()
    if detail is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return detail


@CategoryRouter.post('/', status_code= status.HTTP_201_CREATED)
async def create_category(type: CategoryCreate, db: db_dependency, user: user_dependency):
    new_category= CATEGORIES(**type.dict(), User_id= user.get('id'))
    db.add(new_category)
    db.commit()


@CategoryRouter.put('/{category_id}', status_code= status.HTTP_205_RESET_CONTENT)
async def update_category(category_id: int, db: db_dependency, edit: CategoryCreate, user: user_dependency):
    category= db.query(CATEGORIES).filter(CATEGORIES.id == category_id).filter(CATEGORIES.User_id == user.get('id')).first()
    if category is None:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE)
    category.Name= edit.Name
    category.Description= edit.Description
    db.commit()


@CategoryRouter.delete('/{category_id}', status_code= status.HTTP_102_PROCESSING)
async def delete_category(db:db_dependency, category_id: int, user: user_dependency):
    category= db.query(CATEGORIES).filter(CATEGORIES.id == category_id).filter(CATEGORIES.User_id == user.get('id')).first()
    if category is None:
        raise HTTPException(status.HTTP_204_NO_CONTENT)
    db.delete(category)
    db.commit()