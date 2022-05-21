#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
from http import HTTPStatus

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from app.templatetags.form_utils import calc_prazo
from app.views.megapack import MegaPack

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.urls import reverse_lazy, reverse

from app.models import Channel, Category
from app.mixins import ChannelMixin

from app.utils import get_articles, remove_iv

import django_filters


class ChannelFilter(django_filters.FilterSet):
    class Meta:
        model = Channel
        fields = ["id", "title", "image", "url"]


class List(LoginRequiredMixin, ChannelMixin, ListView):
    """
    List all Channels
    """
    login_url = '/admin/login/'
    template_name = 'channel/list.html'
    model = Channel
    ordering = 'title'
    context_object_name = 'channels'


class Detail(LoginRequiredMixin, ChannelMixin, DetailView):
    """
    Detail of a Channel
    """
    login_url = '/admin/login/'
    model = Channel
    template_name = 'channel/detail.html'
    context_object_name = 'channel'

    def is_in(self, a_list, index):
        if index >= 0:
            return index < len(a_list)
        return False

    def get_context_data(self, **kwargs):
        # print('---- Run CRON JOB my_cron_job')
        # req = get_m3u8_channels({})
        # print(req)
        context = super(Detail, self).get_context_data(**kwargs)
        channel = self.get_object()
        context['list_category'] = Channel.objects.filter(category=channel.category).order_by('title')
        channels_list = [channel_obj.id for channel_obj in Channel.objects.all().order_by('title')]
        index_channel = channels_list.index(channel.id)
        next_index = index_channel + 1
        previous_index = index_channel - 1
        if self.is_in(channels_list, next_index):
            context['next_channel'] = Channel.objects.get(id=channels_list[next_index])
        if self.is_in(channels_list, previous_index):
            context['previous_channel'] = Channel.objects.get(id=channels_list[previous_index])
        return context


def delete_all_channels(request):
    Channel.objects.all().delete()
    return redirect('CHANNEL_list')


def get_channels(request):
    url_channels = 'https://megafilmeshdd.org/categoria/canais/page/{}'

    def title_exists(title):
        qs = Channel.objects.filter(title=title)
        if qs.exists():
            return qs.first()
        return None

    def updator():
        print('-')

    def save_channel(title, rating, image, data_lancamento, url_channel):
        channel = Channel()
        channel.title = title
        channel.image = image
        channel.category = Category.objects.first()
        channel.url = url_channel
        mega = MegaPack()
        try:
            dic_m3u8 = mega.get_info(url_channel)
            channel.link_m3u8 = dic_m3u8['m3u8']
            # channel.code = dic_m3u8['code']
            channel.save()
            print('--- canal salvo: ' + str(channel.title))
        except (Exception,):
            channel.link_m3u8 = None
            channel.save()
            print('--- err ao coletar link m3u8: ' + str(channel.title))

    return get_articles(url_channels, 5, {'class': 'items'}, save_channel, title_exists, updator)


def get_m3u8_channels(request, mega=None):
    # remove_older_program_day()
    # ()
    if not mega:
        mega = MegaPack()
    return get_m3u8_sinal_publico(request, mega)
    # return get_m3u8_megahdd_default(request, mega)


def get_m3u8_megahdd_default(request, mega: MegaPack = None):
    if not mega:
        mega = MegaPack()
    print(time.asctime())
    channels = Channel.objects.all().order_by('title')
    for channel in channels:
        print('-- ', channel.title)
        try:
            dic_m3u8 = mega.get_info(channel.url)
            channel.link_m3u8 = dic_m3u8['m3u8']
            # channel.code = dic_m3u8['code']
            channel.custom_m3u8 = get_custom_m3u8_local(channel)
            channel.save()
        except (Exception,):
            channel.link_m3u8 = None
            channel.save()
            print('--- err ao coletar link m3u8: ' + str(channel.title))
    print(time.asctime())
    return JsonResponse({'message': 'ok'})


def get_m3u8_sinal_publico(request, mega: MegaPack = None):
    if not mega:
        mega = MegaPack()
    print(time.asctime())
    channels = Channel.objects.all().order_by('title')
    for channel in channels:
        url = 'view-source:http://sinalpublico.com/player3/ch.php?canal={}'
        print('-- ', channel.title)
        try:
            dic_m3u8 = mega.get_info_sinal_publico(url.format(channel.code))
            channel.link_m3u8 = dic_m3u8['m3u8']
            while(not calc_prazo(channel.link_m3u8)):
                dic_m3u8 = mega.get_info_sinal_publico(url.format(channel.code))
                channel.link_m3u8 = dic_m3u8['m3u8']
                print(dic_m3u8['m3u8'])
                # channel.code = dic_m3u8['code']
            channel.custom_m3u8 = get_custom_m3u8_local(channel)
            channel.save()
        except (Exception,):
            channel.link_m3u8 = None
            channel.save()
            print('--- err ao coletar link m3u8: ' + str(channel.title))
    print(time.asctime())
    return JsonResponse({'message': 'ok'})


def get_custom_m3u8_local(channel):
    return '/multi/playlist.m3u8?id={}'.format(str(channel.id))


def update_m3u8_channel(request, id):
    channel = Channel.objects.get(id=id)

    url = 'view-source:http://sinalpublico.com/player3/ch.php?canal={}'
    mega = MegaPack()
    try:
        dic_m3u8 = mega.get_info_sinal_publico(url.format(channel.code))
        channel.link_m3u8 = dic_m3u8['m3u8']
        # channel.code = dic_m3u8['code']
        channel.custom_m3u8 = get_custom_m3u8_local(channel)
        channel.save()
    except (Exception,):
        channel.link_m3u8 = None
        channel.save()
        print('--- err ao coletar link m3u8: ' + str(channel.title))
    mega.close()
    return JsonResponse({'message': 'updated'})


def check_m3u8(channel):
    # link = channel.link_m3u8
    # prazo = calc_prazo(link)
    # if not prazo:
    #     update_m3u8_channel({}, channel.id)
       
    # return link
    return channel.link_m3u8


HEADERS = {'origin': 'https://sinalpublico.com', 'referer': 'https://sinalpublico.com/',
           'Accept': '*/*',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'pt-BR, pt;q=0.9, en-US;q=0.8, en;q=0.7',
           'Cache-Control': 'no-cache',
           'Connection': 'keep - alive',
           'Sec-Fetch-Dest': 'empty',
           'Sec-Fetch-Mode': 'cors',
           'Sec-Fetch-Site': 'cross-site',
           'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}


def playlist_m3u8(request):
    dic = dict(request.GET)
    id = dic['id'][0]
    channel = Channel.objects.get(id=id)
    uri_m3u8 = check_m3u8(channel)
    req = requests.get(url=uri_m3u8, headers=HEADERS, verify=False, timeout=(1, 27))
    page = BeautifulSoup(req.text, 'html.parser')
    page_str = str(page.contents[0])
    arr_strings = list(set(remove_iv(re.findall("([^\s]+.ts)", page_str))))
    if len(arr_strings) > 0:
        for i in range(len(arr_strings)):
            new_uri = arr_strings[i]
            page_str = page_str.replace(arr_strings[i],
                                        'http://' + request.META['HTTP_HOST'] + '/multi/ts?link=' + str(
                                            new_uri))
    return HttpResponse(
        content=page_str,
        status=req.status_code,
        content_type=req.headers['Content-Type']
    )


def get_ts(request):
    key = request.GET['link']
    req = requests.get(url=key, stream=True, timeout=(1, 27), headers=HEADERS, verify=False)
    if req.status_code == 200:
        return HttpResponse(
            content=req.content,
            status=req.status_code,
            content_type=req.headers['Content-Type']
        )
    else:
        return HttpResponseNotFound("hello")


def generate_lista_formatted(request):
    f = open("lista2.m3u8", "a")
    f.truncate(0)
    f.write("#EXTM3U\n")
    for ch in Channel.objects.filter(link_m3u8__icontains='.m3u8').distinct().order_by('title'):
        title = ch.title
        id = ch.id
        custom_m3u8 = 'http://' + request.META['HTTP_HOST'] + '/multi/playlist.m3u8?id=' + str(ch.id)
        f.write('#EXTINF:{}, tvg-id="{} - {}" tvg-name="{} - {}" tvg-logo="{}" group-title="{}",{}\n{}\n'.format(
            '-1',
            id,
            title,
            title,
            id,
            ch.image,
            str(ch.category.name),
            title,
            custom_m3u8))
    f.close()
    fsock = open("lista2.m3u8", "rb")
    return HttpResponse(fsock, content_type='text')


def generate_lista_default(request):
    f = open("lista.m3u8", "a")
    f.truncate(0)
    f.write("#EXTM3U\n")
    for ch in Channel.objects.filter(link_m3u8__icontains='.m3u8').distinct().order_by('title'):
        title = ch.title
        custom_m3u8 = 'http://' + request.META['HTTP_HOST'] + '/multi/playlist.m3u8?id=' + str(ch.id)
        f.write('#EXTINF:{}, tvg-id="{} - {}" tvg-name="{} - {}" tvg-logo="{}" group-title="{}",{}\n{}\n'.format(
            ch.id,
            ch.id,
            title,
            title,
            ch.id,
            ch.image,
            'Canais Ao Vivo',
            title,
            custom_m3u8))
    f.close()
    fsock = open("lista.m3u8", "rb")
    return HttpResponse(fsock, content_type='text')



def make_code_channels(request):
    for channel in Channel.objects.all():
        if channel.title.lower().contains('globo'):
            channel.code = channel.title.replace(' ', '').replace('-', '').replace('.', '').replace('_', '').replace('/','').lower()
            channel.code = channel.code.replace('globo', 'bobo')
        channel.code = channel.title.replace(' ', '').replace('-', '').replace('.', '').replace('_', '').replace('/','').lower()
        channel.save()
    return redirect('/')


def get_dump(request):
    channels = [{'title': 'Canal Viva', 'code': 'canalviva', 'image': 'https://i.imgur.com/Ul7v2GN.png', 'url': 'https://megafilmeshdd.org/filmes/canal-viva/'}, {'title': 'ESPN 2', 'code': 'espn2', 'image': 'https://i.imgur.com/MqnN86h.png', 'url': 'https://megafilmeshdd.org/filmes/espn-2/'}, {'title': 'ESPN Extra', 'code': 'espnextra', 'image': 'https://i.imgur.com/QFBtLF6.png', 'url': 'https://megafilmeshdd.org/filmes/espn-extra/'}, {'title': 'SporTV 2', 'code': 'sportv2', 'image': 'https://i.imgur.com/AxVVfyV.png', 'url': 'https://megafilmeshdd.org/filmes/sportv-2/'}, {'title': 'Discovery Kids', 'code': 'discoverykids', 'image': 'https://i.imgur.com/BAQiEpY.png', 'url': 'https://megafilmeshdd.org/filmes/0001-discovery-kids/'}, {'title': 'Disney Junior', 'code': 'disneyjunior', 'image': 'https://i.imgur.com/I0m6rSL.png', 'url': 'https://megafilmeshdd.org/filmes/0001-disney-junior/'}, {'title': 'Tooncast', 'code': 'tooncast', 'image': 'https://i.imgur.com/QCDxeyy.png', 'url': 'https://megafilmeshdd.org/filmes/0001-tooncast/'}, {'title': 'HGTV', 'code': 'hgtv', 'image': 'https://i.imgur.com/n427iTw.png', 'url': 'https://megafilmeshdd.org/filmes/hgtv/'}, {'title': 'Discovery Science', 'code': 'discoveryscience', 'image': 'https://i.imgur.com/ABoDT7p.png', 'url': 'https://megafilmeshdd.org/filmes/discovery-science/'}, {'title': 'Premiere 8', 'code': 'premiere8', 'image': 'https://i.imgur.com/Ko78X9Q.png', 'url': 'https://megafilmeshdd.org/filmes/0001-premiere-8/'}, {'title': 'HBO', 'code': 'hbo', 'image': 'https://i.imgur.com/iszxyjZ.png', 'url': 'https://megafilmeshdd.org/filmes/0001-hbo/'}, {'title': 'TCM', 'code': 'tcm', 'image': 'https://i.imgur.com/hCHHr4F.png', 'url': 'https://megafilmeshdd.org/filmes/0001-tcm/'}, {'title': 'Globo Nordeste', 'code': 'bobonordeste', 'image': 'https://i.imgur.com/mlcNXK0.png', 'url': 'https://megafilmeshdd.org/filmes/0001-globo-nordeste/'}, {'title': 'Arte 1', 'code': 'arte1', 'image': 'https://i.imgur.com/3iIhhU3.png', 'url': 'https://megafilmeshdd.org/filmes/arte-1/'}, {'title': 'Canal Bis', 'code': 'canalbis', 
'image': 'https://i.imgur.com/BM7h3Rr.png', 'url': 'https://megafilmeshdd.org/filmes/canal-bis/'}, {'title': 'Discovery Home & Health', 'code': 'discoveryhomeihealth', 'image': 'https://i.imgur.com/QhIhr7B.png', 'url': 'https://megafilmeshdd.org/filmes/discovery-home-health/'}, {'title': 'Fish TV', 'code': 'fishtv', 'image': 'https://i.imgur.com/BkHhezr.png', 'url': 'https://megafilmeshdd.org/filmes/fish-tv/'}, {'title': 'Paramount Channel', 'code': 'paramount', 'image': 'https://i.imgur.com/tJFv4Qt.png', 'url': 'https://megafilmeshdd.org/filmes/paramount-channel/'}, {'title': 'Record News', 'code': 'recordnews', 'image': 'https://i.imgur.com/cUXoIZt.png', 'url': 'https://megafilmeshdd.org/filmes/record-news/'}, {'title': 'Canal Brasil', 'code': 'canalbrasil', 'image': 'https://i.imgur.com/qCH8yIu.png', 'url': 'https://megafilmeshdd.org/filmes/canal-brasil/'}, {'title': 'CNN Brasil', 'code': 'cnnbrasil', 'image': 'https://i.imgur.com/DJWwds2.png', 'url': 'https://megafilmeshdd.org/filmes/cnn-brasil/'}, {'title': 'Baby TV', 'code': 'babytv', 'image': 'https://i.imgur.com/bCjzJu6.png', 'url': 'https://megafilmeshdd.org/filmes/baby-tv/'}, {'title': 'MTV Live', 'code': 'mtvlive', 'image': 'https://i.imgur.com/SVcwj3W.png', 'url': 'https://megafilmeshdd.org/filmes/mtv-live/'}, {'title': 'TBS', 'code': 'tbs', 'image': 'https://i.imgur.com/exPA3VP.png', 'url': 'https://megafilmeshdd.org/filmes/tbs/'}, {'title': 'Gloobinho', 'code': 'gloobinho', 'image': 'https://i.imgur.com/IrNRwCs.png', 'url': 'https://megafilmeshdd.org/filmes/0002-gloobinho/'}, {'title': 'HBO Mundi', 'code': 'hbomundi', 'image': 'https://i.imgur.com/qNlK8TP.png', 'url': 'https://megafilmeshdd.org/filmes/hbo-mundi/'}, {'title': 'HBO Pop', 'code': 'hbopop', 'image': 'https://i.imgur.com/YmOYQH0.png', 'url': 'https://megafilmeshdd.org/filmes/hbo-pop/'}, {'title': 'HBO Xtreme', 'code': 'hboxtreme', 'image': 'https://i.imgur.com/CK1foHN.png', 'url': 'https://megafilmeshdd.org/filmes/hbo-xtreme/'}, {'title': 'Fox Sports 2', 'code': 'foxsports2', 'image': 'https://i.imgur.com/AlTqVFB.png', 'url': 'https://megafilmeshdd.org/filmes/fox-sports-2/'}, {'title': 'Fox Sports', 'code': 'foxsports', 'image': 'https://i.imgur.com/ZchtiVX.png', 'url': 'https://megafilmeshdd.org/filmes/0001-fox-sports/'}, {'title': 'Band / Rede Bandeirantes', 'code': 'band', 'image': 'https://i.imgur.com/5XHxj5Z.png', 'url': 'https://megafilmeshdd.org/filmes/band-rede-bandeirantes/'}, {'title': 'Band Sports', 'code': 'bandsports', 'image': 'https://i.imgur.com/4wVkerI.png', 'url': 'https://megafilmeshdd.org/filmes/0001-band-sports/'}, {'title': 'Boomerang', 'code': 'boomerang', 'image': 'https://i.imgur.com/YqSVK3o.png', 'url': 'https://megafilmeshdd.org/filmes/0002-boomerang/'}, {'title': 'Canal Sony', 'code': 'sony', 'image': 'https://i.imgur.com/mYXYVFa.png', 'url': 'https://megafilmeshdd.org/filmes/canal-sony/'}, {'title': 'Discovery Theater', 'code': 'discoverytheater', 'image': 'https://i.imgur.com/tOhxlmA.png', 'url': 'https://megafilmeshdd.org/filmes/discovery-theater/'}, {'title': 'E! Entertainment', 'code': 'canale', 'image': 'https://i.imgur.com/MBiZIwt.png', 'url': 'https://megafilmeshdd.org/filmes/e-entertainment/'}, {'title': 'ESPN Brasil', 'code': 'espnbrasil', 'image': 'https://i.imgur.com/NZn1Ukf.png', 'url': 'https://megafilmeshdd.org/filmes/espn-brasil/'}, {'title': 'ESPN', 'code': 'espn', 'image': 'https://i.imgur.com/1BwBo5l.png', 'url': 'https://megafilmeshdd.org/filmes/0002-espn/'}, {'title': 'Food Network', 'code': 'foodnetwork', 'image': 'https://i.imgur.com/uo34Yc1.png', 'url': 'https://megafilmeshdd.org/filmes/food-network/'}, {'title': 'Gloob', 'code': 'gloob', 'image': 'https://i.imgur.com/9uzIdZ8.png', 'url': 'https://megafilmeshdd.org/filmes/0003-gloob/'}, {'title': 'Globo RJ', 'code': 'boborj', 'image': 'https://i.imgur.com/X3w4ByL.png', 'url': 'https://megafilmeshdd.org/filmes/0001-globo-rj/'}, {'title': 'Globo News', 'code': 'globonews', 'image': 'https://i.imgur.com/62RxZZN.png', 'url': 'https://megafilmeshdd.org/filmes/0001-globo-news/'}, {'title': 'GNT', 'code': 'gnt', 'image': 'https://i.imgur.com/gshnVwQ.png', 'url': 'https://megafilmeshdd.org/filmes/gnt/'}, {'title': 'HBO Signature', 'code': 'hbosignature', 'image': 'https://i.imgur.com/sKrCFFU.png', 'url': 'https://megafilmeshdd.org/filmes/hbo-signature/'}, {'title': 'Lifetime', 'code': 'lifetime', 'image': 'https://i.imgur.com/4qZ99HJ.png', 'url': 'https://megafilmeshdd.org/filmes/0003-lifetime/'}, {'title': 'Mais Globosat', 'code': 'maisbobosat', 'image': 'https://i.imgur.com/iPHdiiv.png', 'url': 'https://megafilmeshdd.org/filmes/0001-mais-globosat/'}, {'title': 'Nat Geo Kids', 'code': 'natgeokids', 'image': 
'https://i.imgur.com/hzDcJLq.png', 'url': 'https://megafilmeshdd.org/filmes/nat-geo-kids/'}, {'title': 'Nat Geo Wild', 'code': 'natgeowild', 'image': 'https://i.imgur.com/j2cLJll.png', 'url': 'https://megafilmeshdd.org/filmes/nat-geo-wild/'}, {'title': 'Canal Off', 'code': 'canaloff', 'image': 'https://i.imgur.com/Xi3hhhA.png', 'url': 'https://megafilmeshdd.org/filmes/canal-off/'}, {'title': 'Record TV', 'code': 'recordtv', 'image': 'https://i.imgur.com/fFKRZWh.png', 'url': 'https://megafilmeshdd.org/filmes/0002-record-tv/'}, {'title': 'Band News', 'code': 'bandnews', 
'image': 'https://i.imgur.com/qMghxEY.png', 'url': 'https://megafilmeshdd.org/filmes/0001-band-news/'}, {'title': 'Premiere 7', 'code': 'premiere7', 'image': 'https://i.imgur.com/jQfTTys.png', 'url': 'https://megafilmeshdd.org/filmes/premiere-7/'}, {'title': 'Premiere 6', 'code': 'premiere6', 'image': 'https://i.imgur.com/bdJHk6M.png', 'url': 
'https://megafilmeshdd.org/filmes/premiere-6/'}, {'title': 'Premiere 5', 'code': 'premiere5', 'image': 'https://i.imgur.com/K9dzmSc.png', 'url': 'https://megafilmeshdd.org/filmes/premiere-5/'}, {'title': 'Premiere 4', 'code': 'premiere4', 'image': 'https://i.imgur.com/z27fb5V.png', 'url': 'https://megafilmeshdd.org/filmes/0001-premiere-4/'}, {'title': 'Premiere 3', 'code': 'premiere3', 'image': 'https://i.imgur.com/q8u3RQc.png', 'url': 'https://megafilmeshdd.org/filmes/0001-premiere-3/'}, {'title': 'Premiere 2', 'code': 'premiere2', 'image': 'https://i.imgur.com/4ws22tn.png', 'url': 'https://megafilmeshdd.org/filmes/premiere-2/'}, {'title': 'Premiere Clubes', 'code': 'premiereclubes', 'image': 'https://i.imgur.com/vvBerno.png', 'url': 'https://megafilmeshdd.org/filmes/0001-premiere-clubes/'}, {'title': 'Space', 'code': 'space', 'image': 'https://i.imgur.com/IEpeTlU.png', 'url': 'https://megafilmeshdd.org/filmes/0001-space-hd/'}, {'title': 'Studio Universal / Universal Studio', 'code': 'studiouniversal', 'image': 'https://i.imgur.com/uqyzn3E.png', 'url': 'https://megafilmeshdd.org/filmes/studio-universal-universal-studio/'}, {'title': 'Syfy', 'code': 'syfy', 'image': 'https://i.imgur.com/lZapglS.png', 'url': 'https://megafilmeshdd.org/filmes/0001-syfy/'}, {'title': 'TLC', 'code': 'tlc', 'image': 'https://i.imgur.com/c8r6ETn.png', 'url': 'https://megafilmeshdd.org/filmes/0002-tlc/'}, {'title': 'TNT', 'code': 'tnt', 'image': 'https://i.imgur.com/7Ua1wzG.png', 'url': 'https://megafilmeshdd.org/filmes/tnt/'}, {'title': 'TNT Series', 'code': 'tntseries', 'image': 'https://i.imgur.com/pgleNok.png', 'url': 'https://megafilmeshdd.org/filmes/0001-tnt-series/'}, {'title': 'MTV', 'code': 'mtv', 'image': 'https://i.imgur.com/MAsmCgg.png', 'url': 'https://megafilmeshdd.org/filmes/0001-mtv/'}, {'title': 'National Geographic Channel', 'code': 'natgeo', 'image': 'https://i.imgur.com/j0dzGUT.png', 'url': 'https://megafilmeshdd.org/filmes/national-geographic-channel/'}, {'title': 'Nick Jr.', 'code': 'nickjr', 'image': 'https://i.imgur.com/3Pb0HIP.png', 
'url': 'https://megafilmeshdd.org/filmes/nick-jr/'}, {'title': 'Sexy Hot', 'code': 'sexyhot', 'image': 'https://i.imgur.com/sCARPI4.png', 'url': 'https://megafilmeshdd.org/filmes/sexy-hot/'}, {'title': 'Comedy Central', 'code': 'comedycentral', 'image': 'https://i.imgur.com/xhybWoh.png', 'url': 'https://megafilmeshdd.org/filmes/comedy-central/'}, {'title': 'History 2', 'code': 'history2', 'image': 'https://i.imgur.com/jhxKviv.png', 'url': 'https://megafilmeshdd.org/filmes/history-2/'}, {'title': 'Warner Bros / Warner Channel', 'code': 'warner', 'image': 'https://i.imgur.com/ePyF1DT.png', 'url': 'https://megafilmeshdd.org/filmes/warner-bros-warner-channel/'}, {'title': 'SporTV 3', 'code': 'sportv3', 'image': 'https://i.imgur.com/ukLBdTL.png', 'url': 'https://megafilmeshdd.org/filmes/0001-sportv-3/'}, {'title': 'SporTV', 'code': 'sportv', 'image': 'https://i.imgur.com/gQkGfwg.png', 'url': 'https://megafilmeshdd.org/filmes/0002-sportv/'}, {'title': 'Combate', 'code': 'combate', 'image': 'https://i.imgur.com/3F3aGX3.png', 'url': 'https://megafilmeshdd.org/filmes/0003-combate/'}, {'title': 'Discovery Turbo', 'code': 'discoveryturbo', 'image': 'https://i.imgur.com/uiGu3iE.png', 'url': 'https://megafilmeshdd.org/filmes/discovery-turbo/'}, {'title': 'Telecine Touch', 'code': 'telecinetouch', 'image': 'https://i.imgur.com/wWo3wN5.png', 'url': 'https://megafilmeshdd.org/filmes/0001-telecine-touch/'}, {'title': 'Telecine Premium', 'code': 'telecinepremium', 'image': 'https://i.imgur.com/VmIdMXo.png', 'url': 'https://megafilmeshdd.org/filmes/telecine-premium/'}, {'title': 'Telecine Cult', 'code': 'telecinecult', 'image': 'https://i.imgur.com/43GAgsx.png', 'url': 'https://megafilmeshdd.org/filmes/telecine-cult/'}, {'title': 'MegaPix', 'code': 'megapix', 'image': 'https://i.imgur.com/TLifvJu.png', 'url': 'https://megafilmeshdd.org/filmes/0001-megapix/'}, {'title': 'Investigação Discovery', 'code': 'investigacaodiscovery', 'image': 'https://i.imgur.com/T6l1tiA.png', 'url': 'https://megafilmeshdd.org/filmes/investigacao-discovery/'}, {'title': 'FX', 
'code': 'fx', 'image': 'https://i.imgur.com/EXZHL3e.png', 'url': 'https://megafilmeshdd.org/filmes/0001-fx/'}, {'title': 'Telecine Fun', 'code': 'telecinefun', 'image': 'https://i.imgur.com/vPv68ne.png', 'url': 'https://megafilmeshdd.org/filmes/telecine-fun/'}, {'title': 'Disney XD', 'code': 'disneyxd', 'image': 'https://i.imgur.com/5Ev4Nww.png', 'url': 'https://megafilmeshdd.org/filmes/disney-xd/'}, {'title': 'Disney Channel', 'code': 'disneychannel', 'image': 'https://i.imgur.com/DwUvuaO.png', 'url': 'https://megafilmeshdd.org/filmes/disney-channel/'}, {'title': 'Discovery Channel', 'code': 'discoverychannel', 'image': 'https://i.imgur.com/tvcHqAV.png', 'url': 'https://megafilmeshdd.org/filmes/0001-discovery-channel/'}, {'title': 'Cinemax', 'code': 'cinemax', 'image': 'https://i.imgur.com/S8B0jHK.png', 'url': 'https://megafilmeshdd.org/filmes/cinemax/'}, {'title': 'Cartoon Network', 'code': 'cartoonnetwork', 'image': 'https://i.imgur.com/MmWkVdD.png', 'url': 'https://megafilmeshdd.org/filmes/cartoon-network/'}, {'title': 'AXN', 'code': 'axn', 'image': 'https://i.imgur.com/V40hd4I.png', 'url': 'https://megafilmeshdd.org/filmes/0001-axn/'}, {'title': 'Telecine Action', 'code': 'telecineaction', 'image': 'https://i.imgur.com/h9XBE5j.png', 'url': 
'https://megafilmeshdd.org/filmes/0001-telecine-action/'}, {'title': 'A&E / AeE', 'code': 'aie', 'image': 'https://i.imgur.com/dgMKfj4.png', 'url': 'https://megafilmeshdd.org/filmes/0001-ae-aee/'}, {'title': 'Animal Planet', 'code': 'animalplanet', 'image': 'https://i.imgur.com/1oyAh6i.png', 'url': 'https://megafilmeshdd.org/filmes/0001-animal-planet/'}, {'title': 'AMC', 'code': 'amc', 'image': 'https://i.imgur.com/TmAULwQ.png', 'url': 'https://megafilmeshdd.org/filmes/amc/'}, {'title': 'Telecine Pipoca', 'code': 'telecinepipoca', 'image': 'https://i.imgur.com/ARTvV5X.png', 'url': 'https://megafilmeshdd.org/filmes/telecine-pipoca/'}, {'title': 'Nickelodeon / Nick', 'code': 'nick', 
'image': 'https://i.imgur.com/Schptji.png', 'url': 'https://megafilmeshdd.org/filmes/nickelodeon-nick/'}, {'title': 'Multishow', 'code': 'multishow', 'image': 'https://i.imgur.com/EYsDNG5.png', 'url': 'https://megafilmeshdd.org/filmes/0001-multishow/'}, {'title': 'History Channel', 'code': 'historychannel', 'image': 'https://i.imgur.com/hHg8EmU.png', 'url': 'https://megafilmeshdd.org/filmes/history-channel/'}, {'title': 'HBO Plus', 'code': 'hboplus', 'image': 'https://i.imgur.com/3H6XEDo.png', 'url': 'https://megafilmeshdd.org/filmes/0001-hbo-plus/'}, {'title': 'HBO Family', 'code': 'hbofamily', 'image': 'https://i.imgur.com/1fcviI4.png', 'url': 'https://megafilmeshdd.org/filmes/hbo-family/'}, {'title': 'HBO 2', 'code': 'hbo2', 'image': 'https://i.imgur.com/sbBgj92.png', 'url': 'https://megafilmeshdd.org/filmes/hbo-2/'}, {'title': 'Universal Channel', 'code': 'universalchannel', 'image': 'https://i.imgur.com/dfWYnIJ.png', 'url': 'https://megafilmeshdd.org/filmes/universal-channel/'}, {'title': 'SBT', 'code': 'sbt', 'image': 'https://i.imgur.com/SUR3EdA.png', 'url': 'https://megafilmeshdd.org/filmes/0002-sbt/'}, {'title': 'Globo SP', 'code': 'globosp', 'image': 'https://i.imgur.com/XzH0wwN.png', 'url': 'https://megafilmeshdd.org/filmes/globo-sp/'}, {'title': 'ESPN 3', 'code': 'espn3', 'image': 'https://www.tvmagazine.com.br/imagens/icones/600/espn3.png', 'url': None}, {'title': 'ESPN 4', 'code': 'espn4', 'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/ESPN_4_logo.svg/1280px-ESPN_4_logo.svg.png', 'url': None}]
    
    for ch in channels:
        channel = Channel(title=ch['title'], code=ch['code'], image=ch['image'], url=ch['url'])
        channel.save()
    return redirect('/')