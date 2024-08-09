from confluent_kafka import Producer


class KafkaProxy:
    @staticmethod
    def simple_produce_to_topic(key, value, topic):
        kafka_producer.produce(topic, key=key, value=value)
        kafka_producer.flush()


kafka_producer = Producer({
    'bootstrap.servers': 'localhost:9092'
})
