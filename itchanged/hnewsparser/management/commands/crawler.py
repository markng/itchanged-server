from django.core.management.base import NoArgsCommand
from django.conf import settings
from hnewsparser.models import Story
import django.utils.daemonize
import datetime

class Command(NoArgsCommand):
    """spider"""
    def handle_noargs(self, **options):
        django.utils.daemonize.become_daemon()
        while True:
            stories = Story.objects.all(next_crawl__lt=datetime.datetime.now())
            for story in stories:
                try:
                    story.get()
                except Exception, e:
                    print e
            time.sleep(5)