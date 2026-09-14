from app.rabbitmq import get_rabbitmq_connection


try:
    connection = get_rabbitmq_connection()

    print("RabbitMQ connection successful!")

    connection.close()

except Exception as error:
    print("RabbitMQ connection failed!")
    print(error)