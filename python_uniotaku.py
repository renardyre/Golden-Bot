from bs4 import BeautifulSoup as BS
import re
import requests
import json

def torrents():

    link = 'https://tracker.uniotaku.com/torrents_.php?categoria=0&grupo=0&status=1&ordenar=0&draw=2&columns%5B0%5D%5Bdata%5D=0&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=1&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=2&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=false&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=3&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=4&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=5&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=6&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=7&columns%5B7%5D%5Bname%5D=&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=false&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B8%5D%5Bdata%5D=8&columns%5B8%5D%5Bname%5D=&columns%5B8%5D%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=false&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&start=0&length=50&search%5Bvalue%5D=&search%5Bregex%5D=false&_=1641989449603'
    
    cookie = {'Cookie': 'pass=INSERT_HERE; uid=INSERT_HERE; page-sidebar=true'}
    
    page = requests.get(link, headers=cookie).text
    dic = json.loads(page)
    lista_goldens = dict()

    for i in range(0, len(dic['data'])):
        html = BS(str(dic['data'][i]), 'html5lib')
        torrent_id = re.search('\d{1,5}', html.find('a').get('href')).group(0)
        link_torrent = "https://tracker.uniotaku.com/torrents-details.php?id=" + torrent_id
        link_download = "https://tracker.uniotaku.com/download.php?id=" + torrent_id
        name = html.find_all('a')[0].text
        fansub = html.find_all('a')[1].text if html.find_all('a')[1].text != '' else html.find_all('a')[2].text
        uploader = html.find_all('a')[2].text if html.find_all('a')[1].text != '' else html.find_all('a')[3].text
        categoria = BS(dic['data'][i][1], 'html5lib').find('img').get('alt')
        seeders = BS(dic['data'][i][3], 'html5lib').text
        leechers = BS(dic['data'][i][4], 'html5lib').text
        completado = BS(dic['data'][i][5], 'html5lib').text
        tamanho = BS(dic['data'][i][6], 'html5lib').text
        torrent_page = BS(requests.get(link_torrent, headers=cookie).text, 'html5lib')
        for i in torrent_page.find_all(class_="img-fluid-500"):
            if 'discord' in i.get('src') or 'https://hacchifansub.net/wp-content/uploads/2020/01/capa-hacchi.jpg' in i.get('src') or 'https://i.imgur.com/lesBKL4.png' in i.get('src'):
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



        lista_goldens[torrent_id] = {
                "Nome": name,
                "Pagina": link_torrent,
                "Download": link_download,
                "Fansub": fansub,
                "Uploader": uploader,
                "Categoria": categoria,
                "Seeders": seeders,
                "Leechers": leechers,
                "Completado": completado,
                "Tamanho": tamanho,
                "Imagem": image,
                "Golden": gold,
                "GoldenAte": gold_ate
                }


    with open('uni.json', 'w') as file:
        json.dump(lista_goldens, file, indent=4)

    return lista_goldens

if __name__ == "__main__":
    torrents()
