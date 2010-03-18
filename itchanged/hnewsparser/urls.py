from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'^parse$', 'hnewsparser.views.parse', {}, "hnews-parse"),
)