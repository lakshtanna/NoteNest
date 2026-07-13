from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
NoteNest_Url= 'sqlite:///./NoteNest.db'
Engines= create_engine(NoteNest_Url, connect_args={'check_same_thread': False})
Session_Local= sessionmaker(autoflush= False, autocommit= False, bind= Engines)
Base= declarative_base()