import asyncio
import contextvars
import sys
from typing import Optional, cast

from grpclib.utils import graceful_exit
from grpclib.server import Server, Stream
from grpclib.events import listen, RecvRequest
import datetime
from google.protobuf.timestamp_pb2 import Timestamp
import db_pb2 
import db_grpc 
from models.boxes import *


XRequestId = Optional[str]

request_id: contextvars.ContextVar[XRequestId] = \
    contextvars.ContextVar('x-request-id')

class DatabaseService(db_grpc.DatabaseServiceBase):
    
    async def GetBox(self, stream: Stream[db_pb2.GetBoxRequest, db_pb2.GetBoxResponse]) -> None:
        request = await stream.recv_message()
        b = Boxesdb.findbyid(int(request.id))
        box = db_pb2.Box(id=b._id, name=b.name, price=b.price, description=b.description, category=b.category, quantity=b.quantity, created_at=self.time_mongo2proto(b.created_at))        
        await stream.send_message(db_pb2.GetBoxResponse(box=box))

    async def GetBoxes(self, stream: Stream[db_pb2.GetAllBoxesRequest, db_pb2.GetBoxesResponse]) -> None:
        print('GetBoxes')
        box = []
        allboxes = Boxesdb.findall()
        for b in allboxes:
            box.append(db_pb2.Box(id=b._id, name=b.name, price=b.price, description=b.description, category=b.category, quantity=b.quantity, created_at=self.time_mongo2proto(b.created_at)))      
        print(box)
        await stream.send_message(db_pb2.GetBoxesResponse(box=box))

    async def CreateBox(self, stream: Stream[db_pb2.CreateBoxRequest, db_pb2.CreateBoxResponse]) -> None:
        request = await stream.recv_message()
        box = request.box
        maxid = Boxesdb.maxid()
        box.id = maxid + 1
        new = Boxesdb(_id = box.id, name=box.name, price=box.price, description=box.description, category=box.category, quantity=box.quantity, created_at=self.time_proto2mongo(box.created_at))
        r = new.save()
        resp = db_pb2.CreateBoxResponse()
        if r==0:
            resp.status=1  
        await stream.send_message(resp)

    async def UpdateBox(self, stream: Stream[db_pb2.UpdateBoxRequest, db_pb2.UpdateBoxResponse]) -> None:
        request = await stream.recv_message()
        box = request.box
        box_db = Boxesdb.findbyid(box.id)
        new = Boxesdb(_id = box.id, name=box.name, price=box.price, description=box.description, category=box.category, quantity=box.quantity, created_at=box_db.created_at)
        r = new.save()
        resp = db_pb2.UpdateBoxResponse()
        if r==0:
            resp.status=1  
        await stream.send_message(resp)

    async def DeleteBox(self, stream: Stream[db_pb2.DeleteBoxRequest, db_pb2.DeleteBoxResponse]) -> None:
        request = await stream.recv_message()
        r = Boxesdb.deletebyid(int(request.id))
        resp = db_pb2.DeleteBoxResponse()
        if r==0:
            resp.status=1  
        await stream.send_message(resp)  

    async def GetBoxesInCategory(self, stream: Stream[db_pb2.GetBoxesInCategoryRequest, db_pb2.GetBoxesResponse]) -> None:
        request = await stream.recv_message()
        category = request.category
        box = []
        boxes_in_cat = Boxesdb.findbycat(category)
        for b in boxes_in_cat:
            box.append(db_pb2.Box(id=b._id, name=b.name, price=b.price, description=b.description, category=b.category, quantity=b.quantity, created_at=self.time_mongo2proto(b.created_at)))
        await stream.send_message(db_pb2.GetBoxesResponse(box=box))

    async def GetBoxesInTimeRange(self, stream: Stream[db_pb2.GetBoxesInTimeRangeRequest, db_pb2.GetBoxesResponse]) -> None:
        request = await stream.recv_message()
        start_time = self.time_proto2mongo(request.start_time)
        end_time = self.time_proto2mongo(request.end_time)
        boxes_in_time = Boxesdb.get_in_time_range(start_time, end_time)
        box = []
        for b in boxes_in_time:
            box.append(db_pb2.Box(id=b._id, name=b.name, price=b.price, description=b.description, category=b.category, quantity=b.quantity, created_at=self.time_mongo2proto(b.created_at)))
        await stream.send_message(db_pb2.GetBoxesResponse(box=box))        

    def time_mongo2proto(self, db_time):
        t = db_time.timestamp()
        seconds = int(t)
        nanos = int(t % 1 * 1e9)
        proto_timestamp = Timestamp(seconds=seconds, nanos=nanos)        
        return proto_timestamp

    def time_proto2mongo(self, timestmp):
        time2db = datetime.datetime.fromtimestamp(timestmp.seconds + timestmp.nanos/1e9)
        return time2db


async def on_recv_request(event: RecvRequest) -> None:
    r_id = cast(XRequestId, event.metadata.get('x-request-id'))
    request_id.set(r_id)


async def main(*, host: str = '0.0.0.0', port: int = 50051) -> None:
    server = Server([DatabaseService()])
    listen(server, RecvRequest, on_recv_request)
    with graceful_exit([server]):
        await server.start(host, port)
        print(f'Serving on {host}:{port}')
        await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())