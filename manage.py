import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import *
 
engine = create_engine('sqlite:///users.db', echo=True)
 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
 
user = User("rohan","greylock")
session.add(user)

# commit the record the database
session.commit()