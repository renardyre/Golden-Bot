from bs4 import BeautifulSoup as BS
import re
import requests
import json
import time


class Trackers():
    def save_ids(self, file):
        with open(file, 'w') as f:
            json.dump(sorted(self.torrents_ids), f)

    def compare_with_file(self, file):
        with open(file, 'r') as f:
            file_ids = set(json.load(f))
        result = self.torrents_ids - file_ids
        return sorted(result)

    def get_new_data(self, file, skip_no_seeders=True):
        new = self.compare_with_file(file)
        return self.get_data(ids=new, skip_no_seeders=skip_no_seeders)

    def __str__(self):
        return str(self.torrents_ids)

    def __len__(self):
        return len(self.torrents_ids)

    def __getitem__(self, item):
        return self.torrents_ids[item]


class Shakaw(Trackers):
    def __init__(self, cookie):
        self.cookie = {'Cookie': cookie}
        self.link = "https://tracker.shakaw.com.br/torrents.php?situacao=golden"
        self.torrents_rows = self.get_torrents_rows()
        self.torrents_ids = self.get_ids()

    def get_torrents_rows(self):
        request = requests.get(self.link, headers=self.cookie).text
        page = BS(request, 'html5lib')
        torrents_rows = page.find('tbody').find_all('tr')
        return torrents_rows

    def get_ids(self):
        ids = set()
        for row in self.torrents_rows:
            rows = row.find_all('td')
            torrent_id = re.search('\d{1,4}', rows[1].a.get('href')).group(0)
            ids.add(torrent_id)
        return ids

    def get_data(self, skip_no_seeders=True, ids=None):
        data = {}
        ids_list = self.torrents_ids if ids == None else ids
        for row in self.torrents_rows:
            rows = row.find_all('td')
            torrent_id = re.search('\d{1,4}', rows[1].a.get('href')).group(0)
            if torrent_id not in ids_list: continue
            seeders = rows[6].get_text(strip=True)
            if skip_no_seeders and seeders == "0":
                self.torrents_ids.remove(torrent_id)
                continue
            categoria = rows[0].get_text(strip=True)
            nome = rows[1].get_text(" ", strip=True)
            link_pagina = "https://tracker.shakaw.com.br/torrent.php?torrent_id=" + torrent_id
            link_download = "https://tracker.shakaw.com.br/download.php?torrent_id=" + torrent_id
            pagina_torrent = BS(requests.get(link_pagina, headers=self.cookie).text, 'html5lib')
            link_imagem = pagina_torrent.find(id="imagem_do_torrent").get('src')
            criacao = rows[3].get_text(" ", strip=True)
            arquivos = rows[4].get_text(strip=True)
            tamanho = rows[5].get_text(strip=True)
            leechers = rows[7].get_text(strip=True)
            completado = rows[8].get_text(strip=True)
            fansub = rows[9].get_text(strip=True)
            uploader = rows[10].get_text(strip=True)
            comentarios = rows[11].get_text(strip=True)
            golden = str(rows[1].find_all('span', class_="icone_golden_torrent")) == '[<span class="icone_golden_torrent" title="Gold"></span>]'
            if golden:
                if 'do golden' not in pagina_torrent.text and 'Golden Torrent at' not in pagina_torrent.text:
                    golden_ate = ''
                elif 'do golden' in pagina_torrent.text:
                    golden_ate = pagina_torrent.find(id="h2_sobre_o_periodo_gold").text
                else:
                    golden_ate = re.search('(?<=Golden Torrent até ).*', pagina_torrent.find(id="h2_sobre_o_periodo_gold").text).group(0) 
            else:
                golden_ate = 0

            data[torrent_id] = {
                    "Nome": nome,
                    "Categoria": categoria,
                    "Download": link_download,
                    "Criacao": criacao,
                    "Arquivos": arquivos,
                    "Tamanho": tamanho,
                    "Completado": completado,
                    "Seeders": seeders,
                    "Leechers": leechers,
                    "Fansub": fansub,
                    "Uploader": uploader,
                    "Comentarios": comentarios,
                    "Imagem": link_imagem,
                    "Golden": golden,
                    "GoldenAte": golden_ate,
                    "Pagina": link_pagina
            }
        return data


class Uniotaku(Trackers):
    def __init__(self, cookie):
        self.cookie = {'Cookie': cookie}
        self.link = 'https://tracker.uniotaku.com/torrents_.php?status=1&start=0&length=100'
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
            html = BS(str(torrents_dic[i]), 'html5lib')
            torrent_id = re.search('\d{1,5}', html.find('a').get('href')).group(0)
            ids.add(torrent_id)
        return ids

    def get_data(self, skip_no_seeders=True, ids=None):
        torrents_dic = self.torrents_dic
        data = {}
        ids_list = self.torrents_ids if ids == None else ids
        for i in range(len(torrents_dic)):
            html = BS(str(torrents_dic[i]), 'html5lib')
            torrent_id = re.search('\d{1,5}', html.find('a').get('href')).group(0)
            if torrent_id not in ids_list: continue
            seeders = BS(torrents_dic[i][3], 'html5lib').text
            if skip_no_seeders and seeders == 0:
                self.torrents_ids.remove(torrent_id)
                continue
            link_torrent = "https://tracker.uniotaku.com/torrents-details.php?id=" + torrent_id
            link_download = "https://tracker.uniotaku.com/download.php?id=" + torrent_id
            name = html.find_all('a')[0].text
            fansub = html.find_all('a')[1].text if html.find_all('a')[1].text != '' else html.find_all('a')[2].text
            uploader = html.find_all('a')[2].text if html.find_all('a')[1].text != '' else html.find_all('a')[3].text
            categoria = BS(torrents_dic[i][1], 'html5lib').find('img').get('alt')
            seeders = BS(torrents_dic[i][3], 'html5lib').text
            leechers = BS(torrents_dic[i][4], 'html5lib').text
            completado = BS(torrents_dic[i][5], 'html5lib').text
            tamanho = BS(torrents_dic[i][6], 'html5lib').text
            torrent_page = BS(requests.get(link_torrent, headers=self.cookie).text, 'html5lib')
            for i in torrent_page.find_all(class_="img-fluid-500"):
                if 'discord' in i.get('src') or 'https://hacchifansub.net/wp-content/uploads/2020/01/capa-hacchi.jpg' in i.get('src') or 'https://i.imgur.com/lesBKL4.png' in i.get('src'):
                    image = ''
                    continue
                else:
                    image = i.get('src')
                    break
            if "Gold Coin termina: " in torrent_page.text:
                gold_ate = torrent_page.find(text="Gold Coin termina: ").next.text
                gold = True
            else:
                gold_ate = 0
                gold = False

            data[torrent_id] = {
                    "Nome": name,
                    "Categoria": categoria,
                    "Download": link_download,
                    "Tamanho": tamanho,
                    "Completado": completado,
                    "Seeders": seeders,
                    "Leechers": leechers,
                    "Fansub": fansub,
                    "Uploader": uploader,
                    "Imagem": image,
                    "Golden": gold,
                    "GoldenAte": gold_ate,
                    "Pagina": link_torrent
            }
        return data