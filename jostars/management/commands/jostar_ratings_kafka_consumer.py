import json
from collections import defaultdict
from confluent_kafka import Consumer, KafkaError
from django.conf import settings
from django.core.management.base import BaseCommand
from jostars.models import Rating, Jostar
from django.db import transaction


class Command(BaseCommand):
    help = 'Consumes messages from Kafka in bulk and creates Rating instances'

    def handle(self, *args, **options):
        kafka_consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',  # Replace with your Kafka broker address
            'group.id': 'rating_consumers',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 5000
        })
        kafka_consumer.subscribe([settings.JOSTARS_RATING_KAFKA_TOPIC])

        try:
            while True:
                messages = kafka_consumer.consume(
                    num_messages=settings.KAFKA_RATINGS_CONSUMER_BATCH_SIZE,
                    timeout=1.0
                )

                if not messages:
                    continue

                self.process_batch(messages, kafka_consumer)

        finally:
            kafka_consumer.close()

    def process_batch(self, batch, kafka_consumer):
        ratings_to_create = []
        ratings_to_update = []
        jostar_updates = defaultdict(lambda: {'count': 0, 'sum': 0, 'weight': 1, 'should_effect_average': True})

        # Process each message in the batch
        for msg in batch:
            if msg.error():
                self.stderr.write(f"Error: {msg.error()}")
                continue

            # Decode the message
            message = json.loads(msg.value().decode('utf-8'))
            print(f"Got the message: {message}")
            user_id = message['user_id']
            jostar_id = message['jostar_id']
            rating_value = message['rating']
            weight = message['weight']
            should_effect_average = message['should_effect_average']

            # Check if the rating already exists with the same value
            existing_rating = Rating.objects.filter(
                user_id=user_id,
                jostar_id=jostar_id,
                rating=rating_value
            ).first()

            if existing_rating:
                self.stdout.write(
                    self.style.WARNING(f'Duplicate rating ignored for user {user_id} on jostar {jostar_id}'))
                continue

            # Prepare to create or update the rating
            rating = Rating(user_id=user_id, jostar_id=jostar_id, rating=rating_value)

            # Check if a rating exists for this user and jostar
            existing_rating = Rating.objects.filter(user_id=user_id, jostar_id=jostar_id).first()

            if existing_rating:
                # Update existing rating
                existing_rating.rating = rating_value
                ratings_to_update.append(existing_rating)
                if should_effect_average:
                    jostar_updates[jostar_id]['sum'] += (rating_value - existing_rating.rating)
            else:
                # Create a new rating
                ratings_to_create.append(rating)
                if should_effect_average:
                    jostar_updates[jostar_id]['count'] += 1
                    jostar_updates[jostar_id]['weight'] += weight
                    jostar_updates[jostar_id]['sum'] += (rating_value * weight)

        # Perform batch database operations
        with transaction.atomic():
            # Bulk create new ratings
            if ratings_to_create:
                Rating.objects.bulk_create(ratings_to_create)

            # Bulk update existing ratings
            if ratings_to_update:
                Rating.objects.bulk_update(ratings_to_update, ['rating'])

            # Update each Jostar's statistics using existing values
            for jostar_id, update in jostar_updates.items():
                jostar = Jostar.objects.get(id=jostar_id)

                # Update the Jostar's number_of_ratings and average_rating incrementally
                new_count = jostar.number_of_ratings + update['count']
                new_weight = jostar.number_of_ratings + update['weight']
                new_sum = (jostar.average_rating * jostar.number_of_ratings) + update['sum']
                new_average = new_sum / new_weight if new_weight > 0 else 0

                jostar.number_of_ratings = new_count
                jostar.average_rating = new_average
                jostar.save()

        # Commit the offsets manually after processing
        kafka_consumer.commit(asynchronous=False)

        self.stdout.write(self.style.SUCCESS(f'Processed batch of {len(batch)} messages'))
