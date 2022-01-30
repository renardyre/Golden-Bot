from bs4 import BeautifulSoup
import re
import requests
import json

def torrents():

    link = "https://tracker.shakaw.com.br/torrents.php?situacao=golden"
    cookie = {'Cookie': 'tbshakaw_iddu=INSERT_HERE; tbshakaw_spasse=INSERT_HERE; PHPSESSID=INSERT_HERE'}

    pagina = requests.get(link, headers=cookie).text

    page = BeautifulSoup(pagina, 'html5lib')

    torrents = page.find('tbody').find_all('tr')
    gold = '[<span class="icone_golden_torrent" title="Gold"></span>]'
    
    lista_torrents = []
    lista_goldens = dict() 

    for torrent in torrents:
        colunas = torrent.find_all('td')
        seeders = colunas[6].get_text(strip=True)
        if seeders == "0": continue
        categoria = colunas[0].get_text(strip=True)
        torrent_id = re.search('\d{1,4}', colunas[1].a.get('href')).group(0)
        nome = colunas[1].get_text(" ", strip=True)
        link_pagina = "https://tracker.shakaw.com.br/torrent.php?torrent_id=" + torrent_id
        link_download = "https://tracker.shakaw.com.br/download.php?torrent_id=" + torrent_id
        pagina_torrent = BeautifulSoup(requests.get(link_pagina, headers=cookie).text, 'html5lib')
        link_imagem = pagina_torrent.find(id="imagem_do_torrent").get('src')
        criacao = colunas[3].get_text(" ", strip=True)
        arquivos = colunas[4].get_text(strip=True)
        tamanho = colunas[5].get_text(strip=True)
        leechers = colunas[7].get_text(strip=True)
        completado = colunas[8].get_text(strip=True)
        fansub = colunas[9].get_text(strip=True)
        uploader = colunas[10].get_text(strip=True)
        comentarios = colunas[11].get_text(strip=True)
        golden = str(colunas[1].find_all('span', class_="icone_golden_torrent")) == gold
        if golden:
            if 'do golden' not in pagina_torrent.text and 'Golden Torrent at' not in pagina_torrent.text:
                golden_ate = ''
            elif 'do golden' in pagina_torrent.text:
                golden_ate = pagina_torrent.find(id="h2_sobre_o_periodo_gold").text
            else:
                golden_ate = re.search('(?<=Golden Torrent até ).*', pagina_torrent.find(id="h2_sobre_o_periodo_gold").text).group(0) 
        else:
            golden_ate = 0

        lista_goldens[torrent_id] = {
                "Categoria": categoria,
                "Nome": nome,
                "Pagina": link_pagina,
                "Download": link_download,
                "Imagem": link_imagem,
                "Criacao": criacao,
                "Arquivos": arquivos,
                "Tamanho": tamanho,
                "Seeders": seeders,
                "Leechers": leechers,
                "Completado": completado,
                "Fansub": fansub,
                "Uploader": uploader,
                "Comentarios": comentarios,
                "Golden": golden,
                "GoldenAte": golden_ate
        }
        

    with open('shakaw.json', 'w') as database:
        json.dump(lista_goldens, database, indent=4)

    return lista_goldens

if __name__ == "__main__":
    torrents()
