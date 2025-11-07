import os
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from energybot.web.core.models import ChatUser, Queue, Subscription

LOG_FILE = os.path.join(settings.BASE_DIR.parent.parent, "energybot.log")


def index(request):
    context = {
        "total_users": ChatUser.objects.count(),
        "total_queues": Queue.objects.count(),
        "total_subs": Subscription.objects.count(),
        "queues": Queue.objects.all().prefetch_related("subscriptions"),
    }
    return render(request, "core/index.html", context)


def logs(request):  # pylint: disable=unused-argument
    if not os.path.exists(LOG_FILE):
        return HttpResponse("No logs yet.", content_type="text/plain")
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        data = f.read()[-5000:]  # last 5KB
    return HttpResponse(data, content_type="text/plain")
