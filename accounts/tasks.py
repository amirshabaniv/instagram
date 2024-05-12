from .models import Story
from datetime import datetime, timedelta
from config.celery import app

@app.task
def delete_expired_stories():
    expired_stories = Story.objects.filter(created_at__lte=datetime.now() - timedelta(hours=24))
    expired_stories.delete()