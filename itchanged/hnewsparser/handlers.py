from piston.handler import BaseHandler
from piston.utils import rc
from hnewsparser.models import Story
from hnewsparser.models import Subscription
from django.contrib.auth.models import User
import base64
import random
import string
import simplejson

class StoryHandler(BaseHandler):
    """REST API for Stories"""        
    allowed_methods = ('GET', 'PUT', 'POST','DELETE')
    fields = ('url', 'comphash')
    model = Story
    
    def read(self, request):
        if request.GET.get('url'):    
            story, created = Story.objects.get_or_create(url=request.GET.get('url'))
            story.save()
            return story
        else:
            updated = request.GET.get('updated', False)
            if updated:
                stories = Story.objects.get_user_updated(request.user)
            else:
                stories = Story.objects.filter(subscription__user=request.user)
            return stories
    
    def create(self, request):
        # alias POST to PUT for JS XHR clients (unfortunate, but necessary.)
        return self.update(request)
    
    def update(self, request):
        if request.POST.get('data'):
            # bulkload via json
            data = simplejson.loads(request.POST.get('data'))
            stories = []
            for pair in data:
                stories.append(self.storyadd(request, pair['url'], pair['hash']))
            return stories
        else:
            # single urlparams
            url = request.GET.get('url', request.POST.get('url'))
            comphash = request.GET.get('comphash', request.POST.get('comphash'))
            story = self.storyadd(request, url, comphash)
            return story
    
    def storyadd(self, request, url, comphash):
        """add a single story, subscribe"""
        story, storycreated = Story.objects.get_or_create(url=url)
        if storycreated or story.comphash != comphash:
            story.get()
        if not story.comphash:
            story.comphash = comphash
        story.save()
        subscription, subcreated = Subscription.objects.get_or_create(story=story, user=request.user)
        if not subcreated:
            # subscription wasn't created this time, so this is a read event
            subscription.flag = False
        subscription.comphash = comphash
        subscription.save()
        return story
    
    def delete(self, request):
        """docstring for delete"""
        url = request.GET.get('url', request.POST.get('url', None))
        if url:
            story = Story.objects.get(url=url)
            sub = Subscription.objects.get(story=story, user=request.user)
            sub.delete()
        else:
            Subscription.objects.filter(user=request.user).delete()
        return rc.DELETED
        
class UserHandler(BaseHandler):
    """REST API for user accounts"""
    allowed_methods = ('GET',)
    fields = ('username', 'password')
    model = User
    
    def read(self, request):
        """return a new random username and password"""
        newusername = base64.b64encode(str(random.randint(100000000, 999999999)))
        while len(User.objects.filter(username=newusername)) >= 1:
            newusername = base64.b64encode(str(random.randint(100000000, 999999999)))
        
        chars = string.letters + string.digits
        newpassword = ''
        for i in range(50):
            newpassword = newpassword + random.choice(chars)
        
        user = User()
        user.username = newusername
        user.set_password(newpassword)
        user.save()
        userdetails = { 'username' : newusername, 'password' : newpassword }
        return userdetails