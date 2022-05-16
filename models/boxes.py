from mongoengine import *
import os

def dbconnn(als):
    dbc = None
    try:
        dbc = connect(
            db=os.environ['MONGO_DBNAME'], 
            username=os.environ['MONGO_USERNAME'], 
            password=os.environ['MONGO_PASSWORD'],
            host=os.environ['MONGO_HOST'],
            port=int(os.environ['MONGO_PORT']), 
            uuidRepresentation='standard',
            authentication_source=os.environ['MONGO_AUTH_SOURCE'],
            alias=als,
        )
    except Exception as ex:
        print('cant connect to db {}'.format(ex))
    return dbc

d=dbconnn("default")



class Boxesdb(Document):
    _id = IntField()
    name = StringField(max_length=255)
    description = StringField(max_length=255)
    category = StringField(max_length=255)
    price = IntField()
    quantity = IntField()
    created_at = DateTimeField()
    meta = {"db_alias":"default"}    

    @classmethod
    def maxid(cls):
        return cls.objects().order_by('-_id').limit(1)[0]._id
        
    @classmethod
    def findall(cls):
        return cls.objects()
        
    @classmethod
    def findbyid(cls, id):
        return cls.objects(_id=int(id)).first()

    @classmethod
    def findbycat(cls, cat):
        return cls.objects(category=cat)        

    @classmethod
    def create(cls, id, data):
        return cls.objects(id=id).insert(data)  
        
    @classmethod
    def updatebyid(cls, id, data):
        return cls.objects(id=id).update(data)                 
        
    @classmethod
    def deletebyid(cls, id):
        id = int(id)
        return cls.objects(_id=id).delete()
        
    @classmethod
    def get_in_time_range(cls, start_time, end_time):
        return cls.objects( Q(created_at__gte=start_time) & Q(created_at__lt=end_time) )