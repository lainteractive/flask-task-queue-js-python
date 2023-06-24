To run celery locally on Windows use:

celery -A app.celery worker --loglevel=INFO --pool=solo

To flush Redis server use:

redis-cli FLUSHALL

To run reddis server use:

 redis-server
