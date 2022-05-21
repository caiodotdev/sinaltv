import csv
import json
import random
import string
from base64 import b64encode

import pyimgur
import requests
from bs4 import BeautifulSoup
from django.db.models import (
    CharField,
    TextField,
    IntegerField,
    FloatField,
    EmailField,
    ForeignKey,
    FileField,
    DateTimeField,
    DateField,
    AutoField,
    BooleanField,
    ManyToManyField, ImageField
)
from django.forms.widgets import (
    Textarea,
    NumberInput,
    EmailInput,
    Select,
    TextInput,
    HiddenInput,
    CheckboxInput,
    CheckboxSelectMultiple,
)
from django.http import JsonResponse

from app.models import Channel


def generate_random_string(n):
    """
    Generates a random string of length n
    :param n: Length of string
    :return: Random string
    """
    return ''.join(random.choices(string.ascii_lowercase, k=n))


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    """
    CSV reader for UTF-8 documents
    :param unicode_csv_data: Data of CSV
    :param dialect: Dialect of CSV
    :param kwargs: Other args
    :return:
    """
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [str(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    """
    UTF-8 Encoder
    :param unicode_csv_data:
    :return: Generator of UTF-8 encoding
    """
    for line in unicode_csv_data:
        yield line.encode('utf-8')


def field_to_widget(field):
    if type(field) is CharField:
        if field.choices:
            return Select(attrs={"class": "form-control"})
        return TextInput(attrs={"class": "form-control", "rows": 1})
    if type(field) is TextField:
        return Textarea(attrs={"class": "form-control", "rows": 5})
    if type(field) is AutoField:
        return HiddenInput(attrs={"class": "form-control", "rows": 1})
    if type(field) is IntegerField or type(field) is FloatField:
        return NumberInput(attrs={"class": "form-control"})
    if type(field) is EmailField:
        return EmailInput(attrs={"class": "form-control"})
    if type(field) is ForeignKey:
        return Select(attrs={"class": "form-control"})
    if type(field) is ManyToManyField:
        return CheckboxSelectMultiple(attrs={"class": ""},
                                      choices=((model.id, model) for model in field.related_model.objects.all()))
    if type(field) is BooleanField:
        return CheckboxInput(attrs={"class": ""})
    if type(field) is FileField:
        return TextInput(attrs={"class": "form-control fileinput", "type": "file"})
    if type(field) is ImageField:
        return TextInput(
            attrs={"class": "form-control imageinput", "type": "file", "accept": ".jpg, .jpeg, .png, .ico"})
    if type(field) is DateField:
        return TextInput(attrs={"class": "form-control datepicker date", "type": "date"})
    if type(field) is DateTimeField:
        return TextInput(attrs={"class": "form-control datetimepicker datetime", "type": "date"})
    if field.one_to_one:
        return Select(attrs={"class": "form-control"},
                      choices=((model.id, model) for model in field.related_model.objects.all()))

    return TextInput(attrs={"class": "form-control", "rows": 1})


def generate_bootstrap_widgets_for_all_fields(model):
    return {x.name: field_to_widget(x) for x in model._meta.get_fields()}


def upload_image(request, attribute='file'):
    """
    This method has upload file.
    """
    try:
        CLIENT_ID = "cdadf801dc167ab"
        data = b64encode(request.FILES[attribute].read())
        client = pyimgur.Imgur(CLIENT_ID)
        r = client._send_request('https://api.imgur.com/3/image', method='POST', params={'image': data})
        return r['link']
    except (Exception,):
        return 'http://placehold.it/1024x800'


def upload_file(request, attribute='file'):
    try:
        url_upload = "https://content.dropboxapi.com/2/files/upload"
        name = "/" + str(request.FILES[attribute].name)
        headers_upload = {
            "Authorization": "Bearer M6iN1nYzh_YAAAAAAACHm34PsRKmgPWvVI6uSALYMTqZxGUcopC4pr7K7OkfFfaZ",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": "{\"path\":\"" + name + "\"}"
        }
        data_upload = b64encode(request.FILES[attribute].read())
        response = requests.post(url_upload, headers=headers_upload, data=data_upload)
        print(response.json())
        if response.status_code == 200 or response.status_code == 201:
            url_link = "https://api.dropboxapi.com/2/sharing/create_shared_link"
            headers_link = {
                "Authorization": "Bearer M6iN1nYzh_YAAAAAAACHmqe-TsJhb-Dur_EB09HNKaguknUwnq2a_PprLOwiSS3W",
                "Content-Type": "application/json"
            }
            data_link = {
                "path": "/Apps/pagseguroarquivos" + name,
                "short_url": False
            }
            response_link = requests.post(url_link, headers=headers_link, data=json.dumps(data_link))
            return response_link.json()['url']
        return 'http://placehold.it/1024x800'
    except (Exception,):
        return 'http://placehold.it/1024x800'


def get_page(url, headers):
    req = requests.get(url, headers=headers)
    if req.status_code == 200:
        page = BeautifulSoup(req.text, 'html.parser')
        return page
    return None


HEADERS_MEGA = {
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "cache-control": "no-cache",
    "origin": "https://megafilmeshdd.org",
    "referer": 'https://megafilmeshdd.org/',
}


def get_articles(url_get, pages, div_principal, method, check_article, updator):
    headers = HEADERS_MEGA
    counter = 0
    for i in range(1, int(pages)):
        print('---- page ', str(i))
        try:
            page = get_page(url_get.format(str(i)), headers)
            articles = page.find('div', div_principal).findAll('article')
            for article in articles:
                try:
                    data = article.find('div', {'class': 'data'})
                    title = str(data.find('h3').text)
                    object = check_article(title)
                    if not object:
                        data_lancamento = str(data.find('span').text)
                        poster = article.find('div', {'class': 'poster'})
                        image = str(poster.find('img')['src'])
                        rating = str(poster.find('div', {'class': 'rating'}).text)
                        url_movie = str(poster.find('a')['href'])
                        method(title, rating, image, data_lancamento, url_movie)
                    else:
                        updator(object)
                except(Exception,):
                    counter += 1
                    print('---- Nao conseguiu capturar este article')
                    print('---- Total nao capturados: ', str(counter))
        except(Exception,):
            print('---- Nao conseguiu capturar a page.')
    return JsonResponse(data={'success': 'OK'})


def remove_iv(array_uri):
    for i in range(len(array_uri)):
        if '",IV' in str(array_uri[i]):
            index_iv = str(array_uri[i]).index('",IV=')
            if index_iv >= 0:
                array_uri[i] = str(array_uri[i])[:index_iv]
    return array_uri


def check_m3u8_req(uri, headers):
    try:
        req = requests.get(uri, headers=headers, timeout=2, verify=False)
        if req.status_code == 200:
            return True
        return False
    except (Exception,):
        print('BREAK m3u8')
        return False


def get_img_url(img_tag):
    if img_tag.has_attr('src'):
        img_url = img_tag['src']
    elif img_tag.has_attr('data-src'):
        img_url = img_tag['data-src']
    else:
        img_url = ''
    return img_url


def get_text_type(link):
    uri = str(link.m3u8)
    if 'sd/' in uri:
        return 'SD'
    elif 'hd/' in uri:
        return 'HD'
    else:
        return None


def clean_title(channel):
    title = str(channel.title)
    if 'assistir ' in title.lower():
        if ' ao ' in title.lower():
            title = title[(title.lower().index('assistir ') + len('assistir ')):title.lower().index(' ao ')]
        else:
            title = title[(title.lower().index('assistir ') + len('assistir ')):]
    if ' ao' in title.lower():
        title = title[:title.lower().index(' ao ')]
    if ' online' in title.lower():
        title = title[:title.lower().index(' online')]
    return title
