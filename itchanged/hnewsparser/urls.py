from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from hnewsparser.handlers import StoryHandler

auth = HttpBasicAuthentication(realm="ItChanged API")
ad = { 'authentication': auth }

story_resource = Resource(handler=StoryHandler, **ad)

urlpatterns = patterns('',
    (r'^parse$', 'hnewsparser.views.parse', {}, "hnews-parse"),
    url(r'^api/story/(?P<story_url>[*.]+)$', story_resource),
)