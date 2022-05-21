import time
from urllib.parse import unquote

import jsbeautifier
from jsbeautifier.unpackers import packer, myobfuscate
from jsbeautifier.unpackers.myobfuscate import _filter, CAVEAT

from app.utils import get_page, check_m3u8_req, get_img_url
from app.views.megapack import MegaPack

import re

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import TemplateView, ListView

from app.models import Channel
from app.utils import remove_iv

HEADERS = {'origin': 'https://futemax.gratis', 'referer': 'https://futemax.gratis/',
           'Accept': '*/*',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'pt-BR, pt;q=0.9, en-US;q=0.8, en;q=0.7',
           'Cache-Control': 'no-cache',
           'Connection': 'keep - alive',
           'Sec-Fetch-Dest': 'empty',
           'Sec-Fetch-Mode': 'cors',
           'Sec-Fetch-Site': 'cross-site',
           'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}

URL_FUTEMAX = 'https://futemax.gratis/'


class FutemaxView(LoginRequiredMixin, ListView):
    template_name = 'futemax/list.html'
    login_url = '/admin/login/'
    model = Channel
    context_object_name = 'canais'

    def get_context_data(self, *, object_list=None, **kwargs):
        return super(FutemaxView, self).get_context_data(object_list=object_list, **kwargs)

    def get_queryset(self):
        return self.get_canais()

    def get_canais(self):
        mega = MegaPack()
        mega.browser.get(URL_FUTEMAX)
        page = BeautifulSoup(mega.browser.page_source, 'html.parser')
        canais = []
        if page:
            divs_entries = page.select('div.widget-home>div.item-wd')
            if len(divs_entries) > 0:
                for div in divs_entries:
                    atag = div.find('a')
                    href = atag['href']
                    img_tag = atag.find('img')
                    if img_tag.has_attr('title'):
                        title = img_tag['title']
                    else:
                        title = atag.find('span').get_text()

                    img_url = get_img_url(img_tag)
                    canais.append({
                        'pk': href,
                        'uri': href,
                        'img_url': img_url,
                        'title': title
                    })
        return canais


class ViewChannelFutemax(LoginRequiredMixin, TemplateView):
    template_name = 'futemax/detail.html'
    login_url = '/admin/login/'
    slug_url_kwarg = 'uri'


    def get_m3u8(self, uri):
        try:
            # miner_req = get_page(uri, headers=HEADERS)
            mega = MegaPack()
            mega.browser.get(uri)
            miner_req = BeautifulSoup(mega.browser.page_source, 'html.parser')
            page_source = mega.browser.page_source
            if miner_req:
                # script = None
                # for scr in miner_req.select('script'):
                #     if 'document.referrer' in str(scr):
                #         script = scr
                script = miner_req.select('script')[6]
                content_script = str(script)
                string_source = 'source: "'
                string_m3u8 = '.m3u8'
                string_swarmid = "swarmId: '"
                options_end_swarm = ["max'", "mycdn'"]
                string_end_swarm = options_end_swarm[0]
                swarm_indexes = [m.start() for m in
                                 re.finditer(string_swarmid, content_script)]
                swarm_end_indexes = []
                for opt in options_end_swarm:
                    aux = [m.start() for m in
                           re.finditer(opt, content_script)]
                    if len(aux) > 0:
                        string_end_swarm = opt
                        swarm_end_indexes = aux
                sources_indexes = [m.start() for m in
                                   re.finditer(string_source, content_script)]
                m3u8_indexes = [m.start() for m in
                                re.finditer(string_m3u8, content_script)]
                strings = [
                    content_script[
                    (int(sources_indexes[i]) + len(string_source)):(int(m3u8_indexes[i]) + len(string_m3u8))]
                    for i in range(len(sources_indexes))]
                swarm_id = None
                if len(swarm_end_indexes) > 0:
                    swarm_id = [content_script[
                                (int(swarm_indexes[ind]) + len(string_swarmid)):(
                                        int(swarm_end_indexes[ind]) + (len(string_end_swarm) - 1))] for ind in
                                range(len(swarm_end_indexes))]
                if len(strings) > 0:
                    if swarm_id:
                        if len(swarm_id) > 0:
                            return strings[0], swarm_id[0]
                    return strings[0], ''
                return '', ''
        except (Exception,):
            return '', ''

    def get_links(self):
        temp_url = self.request.GET['uri']
        mega = MegaPack()
        mega.browser.get(temp_url)
        links = []
        page = BeautifulSoup(mega.browser.page_source, 'html.parser')
        a_links = page.select('div.options_iframe>a')
        for atag in a_links:
            uri = atag['data-url']
            m3u8, swarmId = self.get_m3u8(uri)
            if check_m3u8_req(m3u8, headers=self.headers):
                links.append(
                    {
                        'm3u8': m3u8,
                        'swarmId': swarmId
                    }
                )
        return links

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['SITE_URL'] = 'http://' + self.request.META['HTTP_HOST'] + '/'
        links = self.get_links()
        kwargs['links'] = links
        kwargs['source'] = links[0]
        return super(ViewChannelFutemax, self).get_context_data(object_list=object_list, **kwargs)


def playlist_m3u8_futemax(request):
    headers = {'origin': 'https://futemax.live', 'referer': 'https://futemax.live/'}
    uri_m3u8 = request.GET['uri']
    try:
        req = requests.get(url=uri_m3u8, headers=headers)
        page = BeautifulSoup(req.text, 'html.parser')
        page_str = str(page.contents[0])
        arr_strings_without_http = list(set(remove_iv(re.findall("([^\s]+.m3u8)", page_str))))
        if len(arr_strings_without_http) > 0:
            playlist_index = str(uri_m3u8).index('playlist.m3u8')
            prefix = str(uri_m3u8)[:playlist_index]
            for i in range(len(arr_strings_without_http)):
                new_uri = prefix + str(arr_strings_without_http[i])
                page_str = page_str.replace(arr_strings_without_http[i],
                                            'http://' + request.META[
                                                'HTTP_HOST'] + '/' + 'api/futemax/other/playlist.m3u8?uri=' + str(
                                                new_uri))
        else:
            arr_strings = list(set(remove_iv(re.findall("(?P<url>https?://[^\s]+)", page_str))))
            page_str = replace_page_str(arr_strings, page_str, request)
        return HttpResponse(
            content=page_str,
            status=req.status_code,
            content_type=req.headers['Content-Type']
        )
    except (requests.exceptions.ConnectionError,):
        print('erro ao connectar')
        return HttpResponseNotFound()
    except (Exception,):
        return HttpResponseNotFound("hello")


def playlist_other_m3u8_futemax(request):
    headers = {'origin': 'https://futemax.live', 'referer': 'https://futemax.live/'}
    uri_m3u8 = request.GET['uri']
    try:
        req = requests.get(url=uri_m3u8, headers=headers)
        page = BeautifulSoup(req.text, 'html.parser')
        page_str = str(page.contents[0])
        arr_strings = list(set(remove_iv(re.findall("(?P<url>https?://[^\s]+)", page_str))))
        page_str = replace_page_str(arr_strings, page_str, request)
        return HttpResponse(
            content=page_str,
            status=req.status_code,
            content_type=req.headers['Content-Type']
        )
    except (Exception,):
        return HttpResponseNotFound("hello")


def replace_page_str(arr_strings, page_str, request):
    if len(arr_strings) > 0:
        for i in range(len(arr_strings)):
            if not 'key?id=' in str(arr_strings[i]):
                page_str = page_str.replace(arr_strings[i],
                                            'http://' + request.META['HTTP_HOST'] + '/' + 'api/futemax/ts?link=' + str(
                                                arr_strings[i]))
        for uri_ts_coded in arr_strings:
            if 'key?id=' in str(uri_ts_coded):
                page_str = page_str.replace(uri_ts_coded,
                                            'http://' + request.META['HTTP_HOST'] + '/' + 'api/futemax/ts?link=' + str(
                                                uri_ts_coded))
                break
    return page_str


def get_ts_futemax(request):
    key = request.GET['link']
    headers = {'origin': 'https://futemax.live', 'referer': 'https://futemax.live/'}
    try:
        req = requests.get(url=key, stream=True, timeout=60, headers=headers)
        if req.status_code == 200:
            return HttpResponse(
                content=req.content,
                status=req.status_code,
                content_type=req.headers['Content-Type']
            )
        else:
            return HttpResponseNotFound("hello")
    except (Exception,):
        return HttpResponseNotFound("hello")
