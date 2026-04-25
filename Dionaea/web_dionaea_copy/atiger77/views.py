# -*- coding:utf-8 -*-
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http.response import HttpResponse, JsonResponse
import logging


def login(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password'].strip()
        ipaddr = request.META['REMOTE_ADDR']
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s  %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='/tmp/Dionaea.log',
                            filemode='a')
        dst_port = request.get_port()
        logging.warning('Username:{0} Password:{1} ipaddr:{2} Protocol:HTTP Port:{3}'.format(username, password, ipaddr, dst_port))
        return JsonResponse({"messages": u"用户名和密码错误"})
    else:
        return render_to_response("index.html", {}, context_instance=RequestContext(request))
