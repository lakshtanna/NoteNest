from Server import Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey

class USERS(Base):
    __tablename__ = 'users'
    id= Column(Integer, primary_key= True, index= True)
    UserName= Column(String, index= True)
    Email= Column(String,unique= True)
    Hashed_Password= Column(String)
    Is_Admin= Column(Boolean, default= False)

class CATEGORIES(Base):
    __tablename__ = 'category'
    id= Column(Integer, primary_key= True, index= True)
    Name= Column(String) 
    Description= Column(String)  
    User_id= Column(Integer,ForeignKey('users.id'))

class NOTES(Base):
    __tablename__ = 'notes'
    id= Column(Integer, primary_key= True, index= True)
    Title= Column(String)
    Content= Column(String)
    Category_id= Column(Integer,ForeignKey('category.id'))