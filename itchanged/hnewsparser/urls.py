from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from hnewsparser.handlers import StoryHandler
from hnewsparser.handlers import UserHandler

auth = HttpBasicAuthentication(realm="ItChanged API")
ad = { 'authentication': auth }

story_resource = Resource(handler=StoryHandler, **ad)
user_resource = Resource(handler=UserHandler)

urlpatterns = patterns('',
    (r'^parse$', 'hnewsparser.views.parse', {}, "hnews-parse"),
    url(r'^api/story$', story_resource),
    url(r'^api/users$', user_resource ),
    url(r'^changes$', 'hnewsparser.views.history', {}, "history"),
    url(r'^success$', 'django.views.generic.simple.direct_to_template', {}, "success"),
)