from django.contrib.gis.db import models
from django.contrib.auth.models import User
import datetime
import hashlib

class StoryManager(models.Manager):
    """manager for returning users subscribed updated stories"""
    def get_user_updated(self, user):
        return self.filter(subscription__flag=True, subscription__user=user)

class Story(models.Model):
    """news story"""
    url = models.URLField(primary_key=True)
    comphash = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)    
    updated = models.DateTimeField(auto_now_add=True)
    next_crawl = models.DateTimeField(null=True, blank=True)
    objects = StoryManager()
    
    def __unicode__(self):
        """unicode representation"""
        return self.url
    
    def get(self, first=False):
        """crawl, get updates"""
        hnews = self.get_article()
        m = hashlib.md5()
        m.update(hnews[0]['entry-content'].encode('utf-8'))
        self.comphash = m.hexdigest()
        self.updated = datetime.datetime.now()
        if not self.next_crawl:
            self.next_crawl = datetime.datetime.now() + datetime.timedelta(minutes=20) # set first refresh to 20 minutes
        elif self.storyrevision_set.count() <= 1:
            difference = datetime.datetime.now() - self.created
            self.next_crawl = datetime.datetime.now() + (difference * 2) # double backoff
        else:
            difference = datetime.datetime.now() - self.storyrevision_set.order_by('-seen_at')[0].seen_at
            self.next_crawl = datetime.datetime.now() + (difference * 2) # double backoff
        self.save()
        if not StoryRevision.objects.filter(story=self, comphash=m.hexdigest()):
            # hash changed, story updated
            r = StoryRevision()
            r.entry_title = str(hnews[0].get('entry-title', '').encode('utf-8'))
            r.entry_summary = str(hnews[0].get('entry-summary', '').encode('utf-8'))
            r.entry_content = str(hnews[0].get('entry-content', '').encode('utf-8'))
            r.comphash = m.hexdigest()
            r.story = self
            r.save()
            self.next_crawl = datetime.datetime.now() + datetime.timedelta(minutes=20)
            self.save()
            # flag entries
            self.subscription_set.exclude(comphash=r.comphash).update(flag=True)
    
    def get_article(self):
        """get an hnews rep"""
        import urllib2
        import lxml.etree, lxml.html
        from microtron import Parser
        html = urllib2.urlopen(self.url).read()
        tree = lxml.html.document_fromstring(html)
        articles = Parser(tree).parse_format('hnews')
        if not articles:
            articles = Parser(tree).parse_format('hentry')
        return articles

class Subscription(models.Model):
    """user subscription to a story"""
    user = models.ForeignKey(User)
    story = models.ForeignKey(Story)
    comphash = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    flag = models.BooleanField(default=False)
    
    def __unicode__(self):
        """unicoder rep"""
        return "%s %s %s %s" % (self.user, self.story, self.created, self.comphash)

class StoryRevision(models.Model):
    """revision for a story"""
    seen_at = models.DateTimeField(auto_now_add=True)
    entry_title = models.TextField(null=True, blank=True)
    entry_summary = models.TextField(null=True, blank=True)
    entry_content = models.TextField(null=True, blank=True)
    comphash = models.TextField(null=True, blank=True)
    story = models.ForeignKey(Story)
    
    def __unicode__(self):
        """unicode representation"""
        return "%s from %s" % (self.entry_title, self.seen_at)

class Location(models.Model):
    """a specific location"""
    place = models.PointField()

class Area(models.Model):
    """a geographic area"""
    name = models.TextField()
    place = models.MultiPolygonField()