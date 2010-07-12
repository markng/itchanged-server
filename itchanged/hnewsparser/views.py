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
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
    return HttpResponse("%s" % (simplejson.dumps(hnews, sort_keys=True, indent=4, default=dthandler)))
    
def history(request):
    """return a bunch of diff changes"""
    import diff_match_patch
    from textwrap import wrap
    d = diff_match_patch.diff_match_patch()
    url = request.GET['url']
    story, storycreated = Story.objects.get_or_create(url=url)
    if storycreated:
        story.get()
    differences = []
    last = None
    qs = story.storyrevision_set
    lc = 1
    for revision in qs.all():
        if lc == 1:
            last = revision
            differences.append({
                'at' : last.seen_at,
                'difference' : last.entry_content,
                })
        else:
            next = revision
            oldtext = "\r\n".join(wrap(last.entry_content, 90))
            newtext = "\r\n".join(wrap(next.entry_content, 90))
            diff = d.diff_main(newtext, oldtext, checklines=False)
            #diff = d.diff_cleanupSemantic(diff)
            differences.append({
                'at' : next.seen_at,
                'difference' : d.diff_prettyHtml(diff),
                })
            last = next
        lc = lc + 1
    differences.reverse()
    return render_to_response("hnewsparser/history.html", { 'story' : story, 'differences' : differences })