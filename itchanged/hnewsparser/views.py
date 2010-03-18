from django.core import serializers
from django.http import HttpResponse
import lxml.etree, lxml.html
from django.shortcuts import render_to_response
from microtron import Parser
import urllib2
import simplejson

def parse(request):
    """return a parsed article (just JSON for the moment)"""
    url = request.GET['url']
    html = urllib2.urlopen(request.GET['url']).read()
    tree = lxml.html.document_fromstring(html)
    hnews = Parser(tree).parse_format('hnews')
    
    return HttpResponse("%s" % (simplejson.dumps(hnews)))