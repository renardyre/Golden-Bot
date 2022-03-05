from bs4 import BeautifulSoup as BS
import re
import requests
import json
import time
import asyncio
import httpx


class Trackers():
    def save_ids(self, file):
        with open(file, 'w') as f:
            json.dump(sorted(self.torrents_ids), f)

    def compare_with_file(self, file):
        with open(file, 'r') as f:
            file_ids = set(json.load(f))
        result = self.torrents_ids - file_ids
        return sorted(result)

    def get_data(self, ids=None):
        response = asyncio.run(self.get_data_async(ids))
        return response

    def get_new_data(self, file):
        new = self.compare_with_file(file)
        return self.get_data(ids=new)

    def __str__(self):
        return str(self.torrents_ids)

    def __len__(self):
        return len(self.torrents_ids)

    def __getitem__(self, item):
        ids_list = list(self.torrents_ids)
        return ids_list[item]


class Shakaw(Trackers):
    def __init__(self, cookie, url="https://tracker.shakaw.com.br/torrents.php?situacao=golden", skip_no_seeders=True):
        self.cookie = {'Cookie': cookie}
        self.link = url 
        self.skip_no_seeders = skip_no_seeders
        self.torrents_rows = self.get_torrents_rows()
        self.torrents_ids = self.get_ids()

    def get_torrents_rows(self):
        request = requests.get(self.link, headers=self.cookie).text
        page = BS(request, 'html.parser')
        torrents_rows = page.find('tbody').find_all('tr')
        return torrents_rows

    def get_ids(self):
        ids = set()
        for row in self.torrents_rows:
            rows = row.find_all('td')
            seeders = rows[6].get_text(strip=True)
            if self.skip_no_seeders and seeders == "0": continue
            torrent_id = re.search('\d{1,4}', rows[1].a.get('href')).group(0)
            ids.add(torrent_id)
        return ids

    async def get_data_async(self, ids=None):
        data = {}
        tasks = []
        ids_list = self.torrents_ids if ids == None else ids
        for row in self.torrents_rows:
            rows = row.find_all('td')
            torrent_id = re.search('\d{1,4}', rows[1].a.get('href')).group(0)
            if torrent_id not in ids_list: continue

            data[torrent_id] = dict()
            tasks.append(self.page_info(rows, data, torrent_id))
            tasks.append(self.general_info(rows, data, torrent_id))

        done, pending = await asyncio.wait(tasks)
        return data    

    async def general_info(self, rows, db, torrent_id):
        db[torrent_id]['Nome'] = rows[1].get_text(" ", strip=True)
        db[torrent_id]['Categoria'] = rows[0].get_text(strip=True)
        db[torrent_id]['Pagina'] = "https://tracker.shakaw.com.br/torrent.php?torrent_id=" + torrent_id
        db[torrent_id]['Download'] = "https://tracker.shakaw.com.br/download.php?torrent_id=" + torrent_id
        db[torrent_id]['Criacao'] = rows[3].get_text(" ", strip=True)
        db[torrent_id]['Arquivos'] = rows[4].get_text(strip=True)
        db[torrent_id]['Tamanho'] = rows[5].get_text(strip=True)
        db[torrent_id]['Leechers'] = rows[7].get_text(strip=True)
        db[torrent_id]['Seeders'] = rows[6].get_text(strip=True)
        db[torrent_id]['Completado'] = rows[8].get_text(strip=True)
        db[torrent_id]['Fansub'] = rows[9].get_text(strip=True)
        db[torrent_id]['Uploader'] = rows[10].get_text(strip=True)
        db[torrent_id]['Comentarios'] = rows[11].get_text(strip=True)

    async def page_info(self, rows, db, torrent_id):
        link_pagina = "https://tracker.shakaw.com.br/torrent.php?torrent_id=" + torrent_id
        async with httpx.AsyncClient() as client:
            r = await client.get(link_pagina, headers=self.cookie)
        pagina_torrent = BS(r.text, 'html.parser')
        db[torrent_id]['Imagem'] = pagina_torrent.find(id="imagem_do_torrent").get('src')
        golden = str(rows[1].find_all('span', class_="icone_golden_torrent")) == '[<span class="icone_golden_torrent" title="Gold"></span>]'
        if golden:
            if 'do golden' not in pagina_torrent.text and 'Golden Torrent at' not in pagina_torrent.text:
                db[torrent_id]['GoldenAte'] = ''
            elif 'do golden' in pagina_torrent.text:
                db[torrent_id]['GoldenAte'] = pagina_torrent.find(id="h2_sobre_o_periodo_gold").text
            else:
                db[torrent_id]['GoldenAte'] = re.search('(?<=Golden Torrent até ).*', pagina_torrent.find(id="h2_sobre_o_periodo_gold").text).group(0) 
        else:
            db[torrent_id]['GoldenAte'] = 0
        db[torrent_id]['Golden'] = golden


class Uniotaku(Trackers):
    def __init__(self, cookie, url='https://tracker.uniotaku.com/torrents_.php?status=1&start=0&length=100', skip_no_seeders=True):
        self.cookie = {'Cookie': cookie}
        self.link = url
        self.skip_no_seeders = skip_no_seeders
        self.torrents_dic = self.get_torrents_dic()
        self.torrents_ids = self.get_ids()

    def get_torrents_dic(self):
        error = True
        while error:
            time.sleep(3)
            try:
                page = requests.get(self.link, headers=self.cookie).json()
                error = False
            except:
                error = True
        return page['data']

    def get_ids(self):
        torrents_dic = self.torrents_dic
        ids = set()
        for i in range(len(torrents_dic)):
            html = BS(str(torrents_dic[i]), 'html.parser')
            seeders = BS(torrents_dic[i][3], 'html.parser').text
            if self.skip_no_seeders and seeders == 0: continue
            torrent_id = re.search('\d{1,5}', html.find('a').get('href')).group(0)
            ids.add(torrent_id)
        return ids

    async def get_data_async(self, ids=None):
        torrents_dic = self.torrents_dic
        data = {}
        tasks = []
        ids_list = self.torrents_ids if ids == None else ids
        for i in range(len(torrents_dic)):
            html = BS(str(torrents_dic[i]), 'html.parser')
            torrent_id = re.search('\d{1,5}', html.find('a').get('href')).group(0)
            if torrent_id not in ids_list: continue

            data[torrent_id] = dict()
            tasks.append(self.page_info(i, html, data, torrent_id))
            tasks.append(self.general_info(i, html, data, torrent_id))

        done, pending = await asyncio.wait(tasks)
        return data

    async def general_info(self, i, html, db, torrent_id):
        torrents_dic = self.torrents_dic
        db[torrent_id]['Pagina'] = "https://tracker.uniotaku.com/torrents-details.php?id=" + torrent_id
        db[torrent_id]['Download'] = "https://tracker.uniotaku.com/download.php?id=" + torrent_id
        db[torrent_id]['Nome'] = html.find_all('a')[0].text
        db[torrent_id]['Fansub'] = html.find_all('a')[1].text if html.find_all('a')[1].text != '' else html.find_all('a')[2].text
        db[torrent_id]['Uploader'] = html.find_all('a')[2].text if html.find_all('a')[1].text != '' else html.find_all('a')[3].text
        db[torrent_id]['Categoria'] = BS(torrents_dic[i][1], 'html.parser').find('img').get('alt')
        db[torrent_id]['Leechers'] = BS(torrents_dic[i][4], 'html.parser').text
        db[torrent_id]['Seeders'] = BS(torrents_dic[i][3], 'html.parser').text
        db[torrent_id]['Completado'] = BS(torrents_dic[i][5], 'html.parser').text
        db[torrent_id]['Tamanho'] = BS(torrents_dic[i][6], 'html.parser').text

    async def page_info(self, i, html, db, torrent_id):
        link_pagina = "https://tracker.uniotaku.com/torrents-details.php?id=" + torrent_id
        async with httpx.AsyncClient() as client:
            r = await client.get(link_pagina, headers=self.cookie)
        torrent_page = BS(r.text, 'html.parser')
        for i in torrent_page.find_all(class_="img-fluid-500"):
            if 'discord' in i.get('src') or 'https://hacchifansub.net/wp-content/uploads/2020/01/capa-hacchi.jpg' in i.get('src') or 'https://i.imgur.com/lesBKL4.png' in i.get('src'):
                db[torrent_id]['Imagem'] = ''
                continue
            else:
                db[torrent_id]['Imagem'] = i.get('src')
                break
        if "Gold Coin termina: " in torrent_page.text:
            db[torrent_id]['GoldenAte'] = torrent_page.find(text="Gold Coin termina: ").next.text
            db[torrent_id]['Golden'] = True
        else:
            db[torrent_id]['GoldenAte'] = 0
            db[torrent_id]['Golden'] = False