from order_service.order_pb2 import NotificationPayloadProto, OrderProto
from .database import get_session
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from order_service import settings
import logging, asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_consumer(topic, bootstrap_server, consumer_group_id):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_server,
        group_id=consumer_group_id
    )
    # Retry mechanism to keep up the consumer
    while True:
        try:
            await consumer.start()
            logging.info('CONSUMER STARTED')
            break
        except KafkaConnectionError as e:
            logging.error(f'CONSUMER STARTUP FAILED {e}, Retry in 5 seconds')
            await asyncio.sleep(5)
    try:
        async for message in consumer:
            logger.info(f"Received message: {message.value}")

            try:
                # Assume message value is in the format of OrderProto or NotificationPayloadProto
                order_proto = OrderProto()
                order_proto.ParseFromString(message.value)

                logging.info(f"Order Data Proto: {order_proto}")

                # Handle the order data as required
                operation = order_proto.status  # Adjust according to your needs
                order_id = order_proto.id
                item_name = order_proto.item_name
                quantity = order_proto.quantity
                price = order_proto.price

                async with get_session() as session:
                # with Session(engine) as session:
                    if operation == "add":
                        order = Order(
                            id=order_id,
                            item_name=item_name,
                            quantity=quantity,
                            price=price
                        )
                        session.add(order)
                        session.commit()
                        session.refresh(order)
                        logging.info(f"Added order: {order}")
                    
                    elif operation == "delete":
                        order = session.get(Order, order_id)
                        if order:
                            session.delete(order)
                            session.commit()
                            logging.info(f"Deleted order with id: {order_id}")
                        else:
                            logging.warning(f"Order with id: {order_id} not found for deletion")

                    elif operation == "read":
                        order = session.get(Order, order_id)
                        if order:
                            logging.info(f"Read order: {order}")
                        else:
                            logging.warning(f"Order with id: {order_id} not found")

                    elif operation == "update":
                        order = session.get(Order, order_id)
                        if order:
                            order.item_name = item_name
                            order.quantity = quantity
                            order.price = price
                            session.commit()
                            session.refresh(order)
                            logging.info(f"Updated order: {order}")
                        else:
                            logging.warning(f"Order with id: {order_id} not found for update")

            except Exception as e:
                logger.error(f"Error parsing or processing message: {message.value}, Error: {str(e)}")

    except asyncio.CancelledError:
        logger.info("Consumer task was cancelled")
    except Exception as e:
        logger.error(f"Error processing message: {message.value}, Error: {str(e)}")
    finally:
        await consumer.stop()