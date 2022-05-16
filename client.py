import sys
import uuid
import asyncio
import json
from grpclib.client import Channel
from grpclib.events import listen, SendRequest
import datetime
from google.protobuf.timestamp_pb2 import Timestamp
import db_grpc 
import db_pb2 
from server import DatabaseService

def time2proto(date_time_obj):
    t = date_time_obj.timestamp()
    seconds = int(t)
    nanos = int(t % 1 * 1e9)    
    timestamp = Timestamp()
    proto_timestamp = Timestamp(seconds=seconds, nanos=nanos)    
    return proto_timestamp

async def on_send_request(event: SendRequest) -> None:
    request_id = event.metadata['x-request-id'] = str(uuid.uuid4())

async def main(sarg: str = None, param: str = None) -> None:
    channel = Channel('0.0.0.0', 50051)
    listen(channel, SendRequest, on_send_request)
    stub = db_grpc.DatabaseServiceStub(channel)

    if sarg=='-get':
        response = await stub.GetBox(db_pb2.GetBoxRequest(id=int(param)))
        print(response.box, f'status={response.status}')

    elif sarg=='-all':
        response = await stub.GetBoxes(db_pb2.GetAllBoxesRequest())
        boxes = response.box 
        for box in boxes:
            print(f'id: {box.id}, name:{box.name}, price:{box.price}, description:{box.description}, category:{box.category}, quantity:{box.quantity}, created_at:{box.created_at}') 
        print(f'status={response.status}')

    elif sarg=='-crt':
        t = datetime.datetime.now().timestamp()
        seconds = int(t)
        nanos = int(t % 1 * 1e9)    
        timestamp = Timestamp()
        proto_timestamp = Timestamp(seconds=seconds, nanos=nanos)
        box = db_pb2.Box(id=1, name='Lana', price=10, description='pretty', category='present', quantity=8, created_at=proto_timestamp)
        print('box', box) 
        response = await stub.CreateBox(
            db_pb2.CreateBoxRequest(box = box)
        )
        print(f'status={response.status}')
    
    elif sarg=='-upd':
        box = db_pb2.Box(id=int(param), name='Jonh', price=11, description='small', category='mail', quantity=3)
        print(box) 
        response = await stub.UpdateBox(
            db_pb2.UpdateBoxRequest(box = box)
        )
        print(f'status={response.status}')
        
    elif sarg=='-del':
        response = await stub.DeleteBox(
            db_pb2.DeleteBoxRequest(id=int(param))
        )
        print(f'status={response.status}')
        
    elif sarg=='-cat':
        category = param
        response = await stub.GetBoxesInCategory(db_pb2.GetBoxesInCategoryRequest(category=category))
        boxes = response.box 
        for box in boxes:
            print(f'id: {box.id}, name:{box.name}, price:{box.price}, description:{box.description}, category:{box.category}, quantity:{box.quantity}, created_at:{box.created_at}')  
        print(f'status={response.status}')    
    
    elif sarg=='-time':
        start_time = time2proto(datetime.datetime.strptime('2022:05:15 22:07:00', '%Y:%m:%d %H:%M:%S'))
        end_time = time2proto(datetime.datetime.strptime('2022:05:15 22:37:20', '%Y:%m:%d %H:%M:%S'))
        print(start_time, end_time)
        response = await stub.GetBoxesInTimeRange(db_pb2.GetBoxesInTimeRangeRequest(start_time=start_time, end_time=end_time))
        boxes = response.box 
        for box in boxes:
            print(f'id: {box.id}, name:{box.name}, price:{box.price}, description:{box.description}, category:{box.category}, quantity:{box.quantity}, created_at:{box.created_at}')  
        print(f'status={response.status}')
      
    
    channel.close()



if __name__ == '__main__':
    sarg = None
    param = None
    sarg = sys.argv[1]
    if len(sys.argv)>2:
        param = sys.argv[2]
    asyncio.run(main(sarg, param))