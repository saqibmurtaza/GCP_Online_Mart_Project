from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from aiokafka import AIOKafkaProducer
from order_service import settings
from .producer import get_kafka_producer
from .dependencies import get_mock_order_service, get_real_order_service
from .model import Order
from .order_pb2 import NotificationPayloadProto
from order_service.mock_order_service import MockOrderService
import os, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

mock_supabase = os.getenv('MOCK_SUPABASE', 'True').lower() == 'true'

def get_order():
    if mock_supabase:
        return get_mock_order_service()
    return get_real_order_service()

class NotificationPayload(BaseModel):
    order_id: int
    status: str
    user_email: str
    user_phone: str

async def send_notification(payload: NotificationPayload, producer: AIOKafkaProducer,
                            topic:str=settings.TOPIC_ORDER_STATUS):
    await producer.start()
    try:
        payload_proto = NotificationPayloadProto(
            order_id=payload.order_id,
            status=payload.status,
            user_email=payload.user_email,
            user_phone=payload.user_phone
        )
        message = payload_proto.SerializeToString()
        await producer.send_and_wait(topic, message)
        logger.info(f"Notification sent for order_id {payload.order_id}")
    finally:
        await producer.stop()

@app.get("/")
def read_root():
    return {"message": "Order Service"}

@app.post("/create_order", response_model=Order)
async def create_order(
    order: Order,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    service: MockOrderService = Depends(get_order)
):
    order_data = order.model_dump()  # Convert the order instance into a dictionary
    created_order = service.create_order(order_data)
    logging.info(f'Created_Order : {created_order}')

    notification_payload = NotificationPayload(
        order_id=created_order.id,
        status="created",
        user_email="saqibmurtazakhan@gmail.com",
        user_phone="+923171938567"
    )
    await send_notification(notification_payload, producer)

    return created_order

@app.put("/update_order/{order_id}", response_model=Order)
async def update_order(
    order_id: int,
    order: Order,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    service: MockOrderService = Depends(get_order)
):
    update_data = order.model_dump()
    updated_order = service.update_order(order_id, update_data)
    logging.info(f'Updated_Order : {updated_order}')

    if updated_order:
        notification_payload = NotificationPayload(
            order_id=updated_order.id,
            status="updated",
            user_email="saqibmurtazakhan@gmail.com",
            user_phone="+923171938567"
        )
        await send_notification(notification_payload, producer)
        return updated_order
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.delete("/delete_order/{order_id}", response_model=dict)
async def delete_order(
    order_id: int,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    service: MockOrderService = Depends(get_order)
):
    success = service.delete_order(order_id)
    if success:
        notification_payload = NotificationPayload(
            order_id=order_id,
            status="deleted",
            user_email="saqibmurtazakhan@gmail.com",
            user_phone="+923171938567"
        )
        await send_notification(notification_payload, producer)
        return {"message": "Order deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.get("/orders_list", response_model=List[Order])
async def get_orders_list(service: MockOrderService = Depends(get_order)):
    return service.orders_list()
