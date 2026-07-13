from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel,Field,EmailStr
from sqlalchemy.orm import Session
from Server import Session_Local
from typing import Annotated
from Preview import USERS
from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
from jose import jwt,JWTError

UserRouter= APIRouter(prefix= '/users',
                       tags= ['USERS'])



SECURITY_KEY= 'Q0N98862222222223F78318-8WK8-F349J8G978MNCN7207BVW67G6R567NBQ7B6566BCJHAEVLBGA'
ALGORITHM= 'HS256'




bcrypt_contex= CryptContext(schemes= ['bcrypt'], deprecated= 'auto')
Oauth2_bearer= OAuth2PasswordBearer(tokenUrl= 'users/verification')


def get_db():
    db= Session_Local()
    try:
        yield(db)
    finally:
        db.close()    



db_dependency= Annotated[Session,Depends(get_db)]
form_dependency= Annotated[OAuth2PasswordRequestForm,Depends()]
token_dependency= Annotated[str, Depends(Oauth2_bearer)]


class UserCreate(BaseModel):
    username: str= Field(min_length=3, examples= ['Laksh'])
    email: EmailStr= Field(examples= ['example123@email.com'])
    password: str= Field(min_length=4, examples= ['test123'])
    is_admin: bool= Field(default= False)

class TokenCreate(BaseModel):
    access_token: str
    token_type: str   



def users_verification(username: str, password: str, db: db_dependency):
    user= db.query(USERS).filter(USERS.UserName == username).first()

    if not user:
        return False
    if not bcrypt_contex.verify(password, user.Hashed_Password):
        return False
    return user



def encode_token(username: str, id: str, is_admin: bool ,expire_time: timedelta):
    expies= datetime.now(timezone.utc) + expire_time
    payload= {'sub': username, 'id': id, 'is_admin':is_admin ,'exp': expies}
    return jwt.encode(payload, SECURITY_KEY, algorithm= ALGORITHM)


async def decode_token(tokenz: token_dependency):
    print(tokenz)
    print(SECURITY_KEY)
    print(ALGORITHM)
    try:
        payload= jwt.decode(tokenz, SECURITY_KEY, algorithms= ALGORITHM)
        print(payload)
        username: str= payload.get('sub')
        id: str= payload.get('id')
        is_admin: bool= payload.get('is_admin')

        if username is None or id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail= 'User not validated')

        return {'username': username, 'id': id, 'is_admin': is_admin}

    except JWTError as e:
        print('jwterror:', e)
        print(type(e))
        raise



@UserRouter.post('/',status_code= status.HTTP_201_CREATED)
async def create_user(db: db_dependency, identity: UserCreate):
    user= USERS(
        UserName= identity.username,
        Email= identity.email,
        Hashed_Password= bcrypt_contex.hash(identity.password),
        Is_Admin= identity.is_admin

    )
    db.add(user)
    db.commit()
    return 'User signed in successfully'



@UserRouter.post('/verification', response_model= TokenCreate)
async def login_verification(form: form_dependency,db: db_dependency):
    user= users_verification(form.username, form.password, db)

    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail= 'user not verified')
    
    token= encode_token(user.UserName, user.id, user.Is_Admin, timedelta(minutes= 60))

    return {'access_token': token, 'token_type': 'Bearer'}


@UserRouter.get('/see_users')
async def see_users(db: db_dependency):
    users = db.query(USERS).all()
    for user in users:
        user.Hashed_Password = None
    return users