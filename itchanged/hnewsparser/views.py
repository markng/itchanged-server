from django.core import serializers
from django.http import HttpResponse
from django.http import Http404
from models import *
import lxml.etree, lxml.html
from django.shortcuts import render_to_response
from microtron import Parser
import urllib2
import difflib
import simplejson

def json_callback(view_func):
  """if the GET parameter callback is set, wrap response in a function with that name"""
  def _decorator(request, *args, **kwargs):
    try:
      # check for callback, if it's there, modify the return
      callback = request.GET.__getitem__('callback')
      response = view_func(request, *args, **kwargs)
      response.content = callback + '(%s);' % response.content
      return response
    except KeyError, e:
      # callback not found, just return the original function
      return view_func(request, *args, **kwargs)
  return _decorator

@json_callback
def parse(request):
    """return a parsed article (just JSON for the moment)"""
    url = request.GET['url']
    html = urllib2.urlopen(request.GET['url']).read()
    tree = lxml.html.document_fromstring(html)
    hnews = Parser(tree).parse_format('hnews')
    
    return HttpResponse("%s" % (simplejson.dumps(hnews, sort_keys=True, indent=4)))
    
def history(request):
    """return a bunch of diff changes"""
    url = request.GET['url']
    story = Story.objects.get(url=url)
    differences = []
    last = None
    qs = story.storyrevision_set
    if qs.count() > 1:
        lc = 1
        for revision in qs.all():
            if lc == 1:
                last = revision
            else:
                next = revision
                d = difflib.HtmlDiff()
                differences.append(d.make_table(last.entry_content, next.entry_content))
                last = next
            lc = lc + 1
    return render_to_response("hnewsparser/history.html", { 'story' : story, 'differences' : differences })