from confluent_kafka import Producer

from Jostar import settings


class KafkaProxy:
    @staticmethod
    def simple_produce_to_topic(key, value, topic):
        kafka_producer.produce(topic, key=key, value=value)
        kafka_producer.flush()


kafka_producer = Producer({
    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVER_ADDRESS
})
