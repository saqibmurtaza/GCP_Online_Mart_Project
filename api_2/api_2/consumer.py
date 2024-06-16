from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
import json, logging, asyncio
from api_2.database import engine, Session
from api_2.model import Product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_consumer(topic, bootstrapserver, consumer_group_id):
    consumer= AIOKafkaConsumer(topic, bootstrap_servers=bootstrapserver, group_id=consumer_group_id)
# Retry mechanisam to keep up the consumer
    while True:
        try:
            await consumer.start()
            logging.info('********Consumer started.......')
            break
        except KafkaConnectionError as e:
            logging.error(f'CONSUMER STARTUP FAILED {e}, Retry in 5 seconds')
            await asyncio.sleep(5)
        
    try:
        async for message in consumer:
            logger.info(f"Received message: {message.value}")
            product_event= json.loads(message.value.decode('utf-8'))
            operation = product_event.get("operation")
            product_data = product_event.get("data")
            with Session(engine) as session:
                if operation == "add":
                    product = Product(**product_data)
                    session.add(product)
                    session.commit()
                    session.refresh(product)
                    logging.info(f"Added product: {product}")

                elif operation == "delete":
# Ref of producer event " product_event= {"operation" : "delete", "data" : {"product_id": "id"}}"
                    product_id = product_data['product_id'] #extract product_id for deletion, you should access product_data
                    logger.info(f"Product to be deleted with id: {product_id}")
                    product = session.get(Product, product_id)
                    if product:
                        logger.info(f"Found Product: {product}")
                        session.delete(product)
                        session.commit()
                        logger.info(f"Deleted product: {product_id}")
                    else:
                        logger.warning(f"Product with id {product_id} not found for deletion")
    except Exception as e:
        logger.error(f"Error processing message: {message.value}, Error: {str(e)}")
    finally:
        await consumer.stop()

                # elif operation == 'delete':
                #     product_id= product_data.get("id")
                #     logging.info(f'Product to be deleted with Id : {product_id}')
                #     product= session.get(Product, product_id)
                #     logging.info(f'Product to be deleted')
                #     session.delete(product)
                #     session.commit()
                #     logging.info(f'Product with ID:{product_id} deleted successfully')
    #             elif operation == "delete":
    #                 product_id = product_data.get('id')
    #                 logger.info(f"Product to be deleted with id: {product_id}")
    #                 product = await session.get(Product, product_id)
    #                 if product:
    #                     logging.info(f"Found Product: {product}")
    #                     await session.delete(product)
    #                     await session.commit()
    #                     logging.info(f"Deleted product: {product_id}")
    #                 else:
    #                     logging.warning(f"Product with id {product_id} not found for deletion")


    #             elif operation == "update":
    #                 product = session.get(Product, product_data["id"])
    #                 if product:
    #                     product.product_name = product_data["product_name"]
    #                     product.description = product_data["description"]
    #                     product.price = product_data["price"]
    #                     session.commit()
    #                     logging.info(f"Updated product: {product}")

    #             elif operation == "read":
    #                 product = session.get(Product, product_data["id"])
    #                 if product:
    #                     logging.info(f"Read product: {product}")

    # finally:
    #     await consumer.stop()
   
