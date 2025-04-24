# tasks.py
import get_collabs
from app import celery
from celery import Celery

celery = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery.task(bind=True)
def run_collabs(self, access_token, refresh_token, folder_id, exclude_ids):
    # you can self.update_state(state='PROGRESS', meta=…) here
    print("task called")
    get_collabs.main(access_token, refresh_token, folder_id, exclude_ids)
    return "done"