from sqlalchemy.orm import declarative_base

Base = declarative_base()


from models.users import User, OTP 
from models.refresh_token import RefreshToken
