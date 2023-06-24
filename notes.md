In order to test locally you must run celery and redis and flask at the same time. You can use the vscode powershell to run them. Use the strings below to run them

**To run celery locally on Windows use:**

celery -A app.celery worker --loglevel=INFO --pool=solo

**To run reddis server locally use:**

redis-server

**Run flask**

flask run
