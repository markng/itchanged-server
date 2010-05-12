from django.contrib.gis.db import models
from django.contrib.auth.models import User

class StoryManager(models.Manager):
    """manager for returning users subscribed updated stories"""
    def get_user_updated(self, user):
        return self

class Story(models.Model):
    """news story"""
    url = models.URLField(primary_key=True)
    comphash = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        """unicode representation"""
        return self.url
    
    def get(self):
        """crawl, get updates"""
        import urllib2
        import lxml.etree, lxml.html
        from microtron import Parser
        html = urllib2.urlopen(self.url).read()
        tree = lxml.html.document_fromstring(html)
        

class Subscription(models.Model):
    """user subscription to a story"""
    user = models.ForeignKey(User)
    story = models.ForeignKey(Story)
    comphash = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        """unicoder rep"""
        return "%s %s %s %s" % (self.user, self.story, self.updated, self.comphash)

class StoryRevision(models.Model):
    """revision for a story"""
    seen_at = models.DateTimeField(auto_now_add=True)
    entry_title = models.TextField(null=True, blank=True)
    entry_summary = models.TextField(null=True, blank=True)
    entry_content = models.TextField(null=True, blank=True)
    story = models.ForeignKey(Story)
    
    def __unicode__(self):
        """unicode representation"""
        return "%s from %s" % (entry_title, seen_at)

class Location(models.Model):
    """a specific location"""
    place = models.PointField()

class Area(models.Model):
    """a geographic area"""
    name = models.TextField()
    place = models.MultiPolygonField()