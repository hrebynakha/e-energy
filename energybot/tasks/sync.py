"""Sync task file for running Q sync"""

import os
import importlib
import django
from energybot import config
from energybot.helpers.logger import logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "energybot.web.energyweb.settings")
django.setup()

from energybot.web.core.models import Queue

PROVIDER_MODULE_NAME = f"providers.{config.PROVIDER}"
provider = importlib.import_module(PROVIDER_MODULE_NAME)
DEBUG = config.DEBUG


def update_db_queues(queues_info):
    """Update queues in database"""
    for q in queues_info:
        if not Queue.objects.filter(name=q["queue_name"]).exists():
            Queue.objects.create(name=q["queue_name"])
        queue = Queue.objects.get(name=q["queue_name"])
        current_state = queue.current_state
        queue.prev_state = current_state
        queue.current_state = q["slots"]
        queue.save()


def run_sync():
    """Run sync"""
    try:
        queues_info = provider.get_queue_info()
        update_db_queues(queues_info)
        logger.info("Updated queues in database")
    except Exception as e:
        logger.error("Error updating queues in database: %s", e)


if __name__ == "__main__":
    run_sync()
