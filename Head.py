from Preview import *
from Server import *
from fastapi import FastAPI
from noteapp import Category,Notes,Users

NoteNest_Route= FastAPI()
Base.metadata.create_all(bind= Engines)
print("Table_Creation:", list(Base.metadata.tables.keys()))

NoteNest_Route.include_router(Category.CategoryRouter)
NoteNest_Route.include_router(Notes.NoteRouter)
NoteNest_Route.include_router(Users.UserRouter)