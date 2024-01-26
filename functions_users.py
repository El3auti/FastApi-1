from config.db import engine
from schema.user import LoginUser
from models.user import User

def search_user_login(user:LoginUser):
    with engine.connect() as conection:
        user = conection.execute(User.select().where(User.c.username == user.username)).first()._asdict()
        return LoginUser(**user)
    
