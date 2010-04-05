from django.contrib.gis.db import models

class Story(models.Model):
    """news story"""
    url = models.URLField(primary_key=True)
    comphash = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        """unicode representation"""
        return url

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