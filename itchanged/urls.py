from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^itchanged/', include('itchanged.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^images/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.PROJECT_PATH, 'media/images')}, 'images'),
    (r'^stylesheets/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.PROJECT_PATH, 'media/stylesheets')}),
    (r'^downloads/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.PROJECT_PATH, 'media/downloads')}),
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template' : 'home.html'}, "home"),
    (r'^about$', 'django.views.generic.simple.direct_to_template', {'template' : 'about.html'}, "about"),    
    (r'^contact$', 'django.views.generic.simple.direct_to_template', {'template' : 'contact.html'}, "contact"),    
    (r'^', include('hnewsparser.urls')),
    (r'^admin/', include(admin.site.urls)),
)
