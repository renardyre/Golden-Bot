import requests
import json


def torrents():
    page = requests.get('http://tracker.alicepantsu.xyz/apis/api_updates.php').text
    torrents = json.loads(page)

    with open('alicepantsu.json', 'w') as file:
        json.dump(torrents, file, indent=4)

    return torrents


if __name__ == '__main__':
    torrents()