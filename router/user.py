from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException,status
from config.db import engine
from models.user import User
from schema.user import UserCreate,ShowUserJWT,ShowUserFreeData,LoginUser
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from functions_users import search_user_login
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/users",
    tags=["users db practice with oauth"]
)



# Aqui mostramos todas las funciones las cuales un usuario podria hacer sin estar autenticado

@router.post("/create")
async def create_user(user:UserCreate):
    user.password = pwd_context.hash(user.password)
    with engine.connect() as conection:
       conection.execute(User.insert().values(dict(user)))
       conection.commit()
    return {"Success":f"User create :) {user.password}"}


@router.get("/user/{id}")
async def get_user_free_data(id:int):
    with engine.connect() as conection:
        return ShowUserFreeData(**conection.execute(User.select().where(User.c.id == id)).first()._asdict())


@router.get('/')
async def get_users_free_data():
    with engine.connect() as conection:
        return [ShowUserFreeData(**row._asdict()) for row in conection.execute(User.select()).fetchall()]




# Aqui tenemos todos los datos para una autenticacion con jwt,
# la cual la utilizaremos en un futuro para poder ver los datos sensibles de los usuarios

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

oauth2 = OAuth2PasswordBearer(tokenUrl="login")




@router.post('/login')
async def login_user(form:OAuth2PasswordRequestForm = Depends()):
    userauth = search_user_login(LoginUser(password=form.password,username=form.username))

    if not (pwd_context.verify(form.password,userauth.password)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password incorrected, please try again in a few seconds")
    
    access_token = {"sub":userauth.username,
                    "exp":datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                    }
    
    return {"access_token": jwt.encode(access_token,SECRET_KEY,algorithm=ALGORITHM),"token_type":"JWT"}

def auth_user(tk:str = Depends(OAuth2PasswordBearer('/login'))):
    exception = HTTPException(status_code=401,detail="Credenciales de auth invalidas", headers={"WWW-Authenticate":"Bearer"})
    userauth = jwt.decode(tk,SECRET_KEY,ALGORITHM)
    try:
        if userauth['sub'] == "":
            raise exception
    except JWTError:
        raise exception
    
    if userauth['sub'] == "admin":
        return "admin"
    try:
        with engine.connect() as conection:
            return conection.execute(User.select().where(User.c.username == userauth["sub"])).first()._asdict()
    except:
        return False
    
def get_all_users(val = Depends(auth_user)):
    if  val != "admin":
        raise HTTPException(status_code=401,detail="Credenciales de auth invalidas", headers={"WWW-Authenticate":"Bearer"})
    
    with engine.connect() as conection:
        return [ShowUserJWT(**row._asdict()) for row in conection.execute(User.select()).fetchall()]


@router.get('users/protected')
async def get_users_protected_data(users = Depends(get_all_users)):
    return users

def search_me(val = Depends(auth_user)):
    if val == False :
        raise HTTPException(status_code=401,detail="Credenciales de auth invalidas", headers={"WWW-Authenticate":"Bearer"})
    
    return ShowUserJWT(**val)

@router.get('/me')
async def get_me(user = Depends(search_me)):
    return user
     

@router.patch('/edit/{user}')
async def edit_me(now_me:UserCreate,me = Depends(search_me)):
    now_me.password = pwd_context.hash(now_me.password)
    with engine.connect() as conection:
        conection.execute(User.update().where(User.c.id == me.id).values(dict(now_me)))
        conection.commit()
        return ShowUserJWT(**conection.execute(User.select().where(User.c.username == now_me.username)).first()._asdict())




    



