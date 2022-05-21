import os.path
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from django.conf import settings

from app.templatetags.form_utils import calc_prazo
from app.views.engine import EngineModel

SERVER_URL = settings.SERVER_URL

def not_contains_time(link_baixar):
    has_prazo = calc_prazo(link_baixar)
    if not has_prazo:
        return True
    return False


class MegaPack(EngineModel):
    def __init__(self, url=None):
        super(MegaPack, self).__init__()
        self.url = url

    def get_frame(self, list):
        NOT_ALLOWED = ['youtube']
        for iframe in list:
            src = iframe.get_attribute('src')
            if not any(domain in src for domain in NOT_ALLOWED):
                return iframe
        return None

    def create_link(self, text):
        if 'http' not in text:
            return 'http://' + text
        return text

    def remove_unnecessary(self, text):
        # return str(text).replace('-bk', '')
        return text

    def get_code(self, link_baixar):
        if 'hls1' in link_baixar and 'm3u8' in link_baixar:
            return str(link_baixar.split('hls1/')[1].split('.m3u8')[0]).replace('-bk', '')
        return None

    def extract_m3u8(self):
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        try:
            video_tag = soup.find('div', {'id': 'instructions'}).find('video')
            if video_tag.has_attr('data-viblast-src'):
                link_baixar = video_tag['data-viblast-src']
                link_baixar = self.cut_url(link_baixar)
                link_m3u8 = self.create_link(link_baixar)
                code_channel = self.get_code(link_baixar)
                return {'m3u8': link_m3u8, 'code': code_channel}
            else:
                raise Exception('Nao encontrei m3u8')
            # player = soup.find('div', {'id': 'instructions'}).find('div', {'id': 'RedeCanaisPlayer'})
            # if player.has_attr('baixar'):
            #     link_baixar = player['baixar']
            #     link_baixar = self.cut_url(link_baixar)
            #     return {'m3u8': self.create_link(link_baixar), 'code': self.get_code(link_baixar)}
            # links = [link for link in soup.find_all('a') if 'm3u9' in link['href']]
            # if links:
            #     link_baixar = links[0]['href']
            #     link_baixar = self.cut_url(link_baixar)
            #     return {'m3u8': self.create_link(link_baixar), 'code': self.get_code(link_baixar)}
        except (Exception,):
            print('--- Nao encontrou div#instructions')
        return None

    def get_info_impl(self, url, extract_m3u8):
        if url:
            self.url = url
        self.browser.get(self.url)
        return extract_m3u8()

    def get_info_sinal_publico(self, url_view_source=None):
        url_no_view = url_view_source
        if 'view-source:' in url_view_source:
            url_no_view = url_view_source[str(url_view_source).index('view-source:') + 12:]
        self.url = url_view_source
        # Burlar CloudFlare
        self.browser.get(url_no_view)
        time.sleep(10)
        # Acessar View_source
        self.browser.get(self.url)
        content_view_source = self.browser.page_source
        page_text = BeautifulSoup(content_view_source, 'html.parser').text
        page_text = page_text[page_text.index('<script'):]
        # escre o conteudo criptografado para ser executado no navegador
        file = open(os.path.join('app', 'templates', 'canal.html'), 'w')
        file.write('<meta charset="utf-8" />\n ' + str(page_text))
        file.close()
        # pega o conteudo descriptografado pelo navegador
        self.browser.get(SERVER_URL + '/scrap-canal/')
        dic = self.extract_m3u8()
        # if not_contains_time(dic['m3u8']):
        #     while (not_contains_time(dic['m3u8'])):
        #         dic = self.extract_m3u8()
        #         print(dic['m3u8'])
        # print(dic['m3u8'])
        return dic

    def close(self):
        self.browser.close()
        self.browser.quit()

    def get_info(self, url=None):
        if url:
            self.url = url
        self.browser.get(self.url)
        frame = self.get_frame(self.browser.find_elements(By.CLASS_NAME, "rptss"))
        if frame:
            self.browser.switch_to.frame(frame)
        else:
            print('Nao encontrou o frame de video.')
        return self.extract_m3u8()

    def cut_url(self, url: str):
        word = 'download.php?vid='
        if word in url:
            index = url.index(word) + len(word)
            url = str(url[index:])
        return url

    def get_info_futemax(self, url):
        if url:
            self.url = url
        self.browser.get(self.url)
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')

        frame = self.get_frame(self.browser.find_elements(By.CLASS_NAME, "rptss"))
        if frame:
            self.browser.switch_to.frame(frame)
        else:
            print('Nao encontrou o frame de video.')
        return self.extract_m3u8()
