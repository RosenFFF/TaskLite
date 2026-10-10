import click
import json
from tasklite.store import TaskStore
from tasklite.queue import TaskQueue
from tasklite.worker import Worker
from tasklite.scheduler import schedule_job

@click.group()
def cli():
    pass

@cli.command()
@click.option('--handler', required=True)
@click.option('--payload', default='{}')
@click.option('--priority', default='normal')
@click.option('--queue', default='default')
def enqueue(handler, payload, priority, queue):
    store = TaskStore()
    tq = TaskQueue(store)
    try:
        p = json.loads(payload)
        job = tq.enqueue(handler=handler, payload=p, priority=priority, queue=queue)
        click.echo(f"Enqueued job {job.id}")
    except Exception as e:
        click.echo(str(e), err=True)
        raise click.Abort()

@cli.command()
@click.option('--queue', default='default')
@click.option('--burst', is_flag=True)
def worker(queue, burst):
    store = TaskStore()
    w = Worker(store)
    w.run(queue=queue, burst=burst)

@cli.command()
@click.argument('job_id')
def status(job_id):
    store = TaskStore()
    tq = TaskQueue(store)
    try:
        st = tq.get_status(job_id)
        click.echo(json.dumps(st))
    except Exception as e:
        click.echo(str(e), err=True)
        raise click.Abort()

@cli.command()
@click.argument('job_id')
def retry(job_id):
    store = TaskStore()
    tq = TaskQueue(store)
    try:
        tq.retry_job(job_id)
        click.echo(f"Retried job {job_id}")
    except Exception as e:
        click.echo(str(e), err=True)
        raise click.Abort()

@cli.command()
@click.option('--handler', required=True)
@click.option('--scheduled-at', required=True)
def schedule(handler, scheduled_at):
    store = TaskStore()
    tq = TaskQueue(store)
    try:
        job = schedule_job(tq, handler, scheduled_at)
        click.echo(f"Scheduled job {job.id}")
    except Exception as e:
        click.echo(str(e), err=True)
        raise click.Abort()

@cli.command()
def list():
    store = TaskStore()
    jobs = store.list_jobs()
    for job in jobs:
        click.echo(f"{job.id} - {job.status.value}")

@cli.command()
@click.argument('job_id')
def cancel(job_id):
    store = TaskStore()
    tq = TaskQueue(store)
    try:
        tq.cancel_job(job_id)
        click.echo(f"Cancelled job {job_id}")
    except Exception as e:
        click.echo(str(e), err=True)
        raise click.Abort()

@cli.command()
def stats():
    pass

if __name__ == '__main__':
    cli()
