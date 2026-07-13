from fastapi import APIRouter,Depends,status,HTTPException
from pydantic import Field,BaseModel
from Server import Session_Local
from sqlalchemy.orm import Session
from typing import Annotated
from Preview import NOTES,CATEGORIES
from .Users import decode_token


NoteRouter= APIRouter(prefix= '/notes',
                      tags=['NOTES'])


def get_db():
    db= Session_Local()
    try:
        yield(db)
    finally:
        db.close()    


db_dependency= Annotated[Session, Depends(get_db)]
user_dependency= Annotated[dict, Depends(decode_token)]

class NoteCreate(BaseModel):
    Title: str= Field(min_length= 3, examples= ["Pydantics"])
    Content: str= Field(min_length=3, examples= ["Notes related to Field"])
    Category_id: int



@NoteRouter.get('/', status_code= status.HTTP_200_OK)
async def get_notes(db: db_dependency, user: user_dependency):
    category= db.query(CATEGORIES).filter(CATEGORIES.User_id == user.get('id')).all()

    notes=[]

    for cat in category:
        notes.extend(db.query(NOTES).filter(NOTES.Category_id == cat.id).all())

    return notes



@NoteRouter.get('/{Note_id}', status_code= status.HTTP_200_OK)
async def get_category(Note_id: int, db: db_dependency, user: user_dependency):
    category = db.query(CATEGORIES).filter(CATEGORIES.User_id == user.get('id')).all()

    notes=[]

    for cat in category:
        category_notes=db.query(NOTES).filter(NOTES.Category_id == cat.id).all()

        notes.extend(category_notes)

    for note in notes:
        if note.id == Note_id:
            return note
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail='note not found')    


    
    
@NoteRouter.post('/', status_code= status.HTTP_201_CREATED)
async def create_note(type: NoteCreate, db: db_dependency, user: user_dependency):
    category= db.query(CATEGORIES).filter(CATEGORIES.id == type.Category_id, CATEGORIES.User_id == user.get('id')).first()
    if category is None: 
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail= 'category not found')
    note= NOTES(**type.dict())
    db.add(note)
    db.commit()


@NoteRouter.put('/{note_id}', status_code= status.HTTP_205_RESET_CONTENT)
async def update_note(note_id: int, db: db_dependency, edit: NoteCreate, user: user_dependency):
    
    note= db.query(NOTES).join(CATEGORIES).filter(NOTES.id == note_id, NOTES.Category_id == CATEGORIES.id, CATEGORIES.User_id == user.get('id')).first()

    if note is None:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE)
    
    note.Title= edit.Title
    note.Content= edit.Content
    note.Category_id= edit.Category_id
    db.commit()


@NoteRouter.delete('/{note_id}', status_code= status.HTTP_102_PROCESSING)
async def delete_note(db:db_dependency, note_id: int, user: user_dependency):
    note= db.query(NOTES).join(CATEGORIES).filter(NOTES.id == note_id, NOTES.Category_id == CATEGORIES.id, CATEGORIES.User_id == user.get('id')).first()   

    if note is None:
        raise HTTPException(status.HTTP_204_NO_CONTENT)
    
    db.delete(note)
    db.commit()



  