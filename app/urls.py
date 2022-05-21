from django.urls import path, include
from django.views.generic import TemplateView

from app import conf
from app.urls_api import api_urlpatterns
from app.views.channel import playlist_m3u8, get_ts

urlpatterns = []

urlpatterns += [
    path('', include('rest_auth.urls')),
    path('registration/', include('rest_auth.registration.urls'))
]

from app.views import futemax, channel

urlpatterns += [
    # channel
    path(
        '',
        channel.List.as_view(),
        name=conf.CHANNEL_LIST_URL_NAME
    ),
    path(
        'channel/<int:pk>/',
        channel.Detail.as_view(),
        name=conf.CHANNEL_DETAIL_URL_NAME
    ),
    path(
        'get-channels',
        channel.get_channels,
        name='get_channels'
    ),
    path(
        'delete-channels',
        channel.delete_all_channels,
        name='delete_all_channels'
    ),
    path(
        'get-channels-m3u8',
        channel.get_m3u8_channels,
        name='get_channels_m3u8'
    ),
    path(
        'get-m3u8-channel/<int:id>/',
        channel.update_m3u8_channel,
        name='get_m3u8_channel'
    ),
    path(
        'lista.m3u8',
        channel.generate_lista_default,
        name='gen_lista'
    ),
    path(
        'lista2.m3u8',
        channel.generate_lista_formatted,
        name='gen_lista_personal'
    ),
    path('multi/playlist.m3u8', playlist_m3u8, name='playlist_m3u8'),
    path('multi/ts', get_ts, name='get_ts'),
    path('scrap-canal/',
         TemplateView.as_view(template_name='canal.html')),
    path('code-channels/',
            channel.make_code_channels, name='make_code_channels'),
    path('getdump/', channel.get_dump),
]

urlpatterns += api_urlpatterns
