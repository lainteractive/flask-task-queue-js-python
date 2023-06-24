from celery.result import AsyncResult
from celery import Celery
from redis import ConnectionPool, Redis

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
redis_connection_pool = ConnectionPool.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))

# CELERY SETUP


# CELERY SETUP


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=os.environ.get('REDIS_URL', 'redis://localhost:6379'),
        broker=os.environ.get('REDIS_URL', 'redis://localhost:6379')
    )
    celery.conf.update(
        app.config,
        BROKER_POOL_LIMIT=19  # Add this line to set the connection pool limit
    )
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

def init_celery(app):
    celery = make_celery(app)


    app.config['CELERY_REDIS_MAX_CONNECTIONS'] = 19
    app.config['CELERY_REDIS_CONNECTION_TIMEOUT'] = 60

    celery.conf.task_soft_time_limit = 90  # Soft time limit in seconds
    celery.conf.task_time_limit = 120  # Hard time limit in seconds

    celery.conf.update(app.config)
    return celery


celery = make_celery(app)

class CloseConnectionTask(celery.Task):
    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # Close Redis connection
        backend_url = celery.backend.url
        connection_pool = ConnectionPool.from_url(backend_url)
        redis_conn = Redis(connection_pool=connection_pool)
        redis_conn.connection_pool.disconnect()

# CELERY ROUTES

@app.route('/task_status/<task_id>')
def task_status(task_id):
    task = AsyncResult(task_id, app=celery)
    print(task.state)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result
        }  
    else:
        response = {
                'state': task.state,
                'status': str(task.result),
                'traceback': task.traceback
            }
    return jsonify(response)



#Queued Tasks


@app.route('/start_ai', methods=['POST'])
@login_required
def start_ai():

    prompt = request.json['prompt']    
    task = end_ai.delay(prompt)
    return jsonify({'task_id': task.id}), 202

@celery.task(bind=True,base=CloseConnectionTask)
def end_ai(self, prompt):
  tries = 0
  while tries < 3:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=[
                   {"role": "user", "content": query}
                ]
            )
            response = completion.choices[0].message.content
            break  
        except:
            tries += 1
            if tries >= 3:    
                response = 'AI Error'
    response = response.replace("\n", "<br>")
    result = response
    return result
