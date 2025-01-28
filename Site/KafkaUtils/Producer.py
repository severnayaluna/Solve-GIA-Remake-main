from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic


admin_client = AdminClient({
    'bootstrap.servers': 'localhost:9092',
})
admin_client.create_topics([NewTopic('bot')])

producer = Producer(
    {
    'bootstrap.servers': 'localhost:9092',
    }
)
