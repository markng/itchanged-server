from piston.handler import BaseHandler
from piston.utils import rc
from hnewsparser.models import Story
from hnewsparser.models import Subscription
from django.contrib.auth.models import User
import base64
import random
import string

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
            stories = Story.objects.get_user_updated(request.user)
            return stories
    
    def create(self, request):
        # alias POST to PUT for JS XHR clients (unfortunate, but necessary.)
        return self.update(request)
    
    def update(self, request):
        url = request.GET.get('url', request.POST.get('url'))
        story, storycreated = Story.objects.get_or_create(url=url)
        if storycreated or story.comphash != request.GET.get('comphash', request.POST.get('comphash')):
            story.get()
        story.comphash = request.GET.get('comphash', request.POST.get('comphash')) # blindly trust, for the moment. FIX; send to celery queue to be processed
        story.save()
        subscription, subcreated = Subscription.objects.get_or_create(story=story, user=request.user)
        if not subcreated:
            # subscription wasn't created this time, so this is a read event
            subscription.flag = False
        subscription.comphash = request.GET.get('comphash', request.POST.get('comphash'))
        subscription.save()
        return story
    
    def delete(self, request):
        """docstring for delete"""
        url = request.GET.get('url', request.POST.get('url'))
        story = Story.objects.get(url=url)
        sub = Subscription.objects.get(story=story, user=request.user)
        sub.delete()
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