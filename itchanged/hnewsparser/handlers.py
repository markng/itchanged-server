from piston.handler import BaseHandler
from hnewsparser.models import Story
from django.contrib.auth.models import User
import base64
import random
import string

class StoryHandler(BaseHandler):
    """REST API for Stories"""        
    allowed_methods = ('GET', 'PUT', 'POST')
    fields = ('url', 'comphash')
    model = Story
    
    def read(self, request):
        story, created = Story.objects.get_or_create(url=request.GET.get('story_url'))
        story.save()
        return story
    
    def create(self, request):
        # alias POST to PUT for JS XHR clients (unfortunate, but necessary.)
        return self.update(request)
    
    def update(self, request):
        url = request.GET.get('url', request.POST.get('url', request.PUT.get('url')))
        story, created = Story.objects.get_or_create(url=request.GET.get('url'))
        story.comphash = request.PUT.get('comphash') # blindly trust, for the moment. FIX; send to celery queue to be processed
        story.save()
        # TODO : attach to users list of stories
        return story
        
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