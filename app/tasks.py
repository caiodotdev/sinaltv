import time

from celery import shared_task

from .views.channel import get_m3u8_channels
from .views.megapack import MegaPack
from .celery import app

"""
This module defines various Celery.
"""


@shared_task()
def fetch_channels():
    mega = MegaPack()
    print('---- Starting collect channels -----')
    print(time.asctime())
    get_m3u8_channels({}, mega)
    print(time.asctime())
    print('---- Finish collect channels ------: ')
    mega.close()
