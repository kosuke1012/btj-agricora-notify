import requests
import yaml
from time import sleep
from bs4 import BeautifulSoup


def getplayer(souptext, gameid, lineclass):
    htmlallsoup = BeautifulSoup(souptext, 'lxml')
    titlelist = htmlallsoup.find_all(class_=lineclass)
    for title in titlelist:
        if title.find(class_="clIcone").string == gameid:
            for tagall in title:
                tagsoup = BeautifulSoup(str(tagall), 'lxml')
                for tag in tagsoup:
                    if len(tag.find_all("span")) != 0:
                        spans = tag.find_all("span")
                        for span in spans:
                            if span is not None:
                                spansoup = BeautifulSoup(str(span), 'lxml')
                                if "font-weight:bold" in spansoup.find("span").get("style"):
                                    now_player = spansoup.find("span").string
                                    return now_player


if __name__ == '__main__':

    f = open('conf.yml', 'r+')
    conf = yaml.load(f)

    USER = conf['userid']
    PASS = conf['password']
    PACTION = 'login'
    GAMES = conf['games']
    POLLRATE = 10

    session = requests.session()

    login_info = {
            'pAction': PACTION,
            'username': USER,
            'password': PASS
            }

    # config for LINE notify
    line_notify_token = conf['lineaccesstoken']
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + line_notify_token}

    url_login = 'http://www.boiteajeux.net/gestion.php'
    res = session.post(url_login, data=login_info)
    res.raise_for_status()

    old_players = []
    for i, game in enumerate(GAMES):
        old_player = getplayer(res.text, str(game['id']), 'clLigne1')
        if old_player is None:
            old_player = getplayer(res.text, str(game['id']), 'clLigne2')
        old_players.append(old_player)


    while True:
        sleep(POLLRATE)
        res = session.post(url_login, data=login_info)
        res.raise_for_status()
        now_players = []
        for i, game in enumerate(GAMES):
            now_player = getplayer(res.text, str(game['id']), 'clLigne1')
            if now_player is None:
                now_player = getplayer(res.text, str(game['id']), 'clLigne2')

            now_players.append(now_player)

            if now_players[i] != old_players[i]:
                message = 'On game ' + game['name'] + ',\nplayed by ' + str(old_players[i]) + '.\n' + str(now_players[i]) + '\'s turn.'
                payload = {'message': message}
                line_notify = requests.post(line_notify_api,
                                            data=payload, headers=headers)
                old_players[i] = now_players[i]
