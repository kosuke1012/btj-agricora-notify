import requests
import yaml
import re
from bs4 import BeautifulSoup

def get_gameid(souptext, gamename):
    htmlallsoup = BeautifulSoup(souptext, 'lxml')
    alst = htmlallsoup.find_all("a", text=re.compile(gamename))
    gamedict = dict()
    for game in alst:
        gameid = game.parent.parent.find(class_="clIcone").string
        gamename = game.string
        gamedict[int(gameid)]=str(gamename)
    return gamedict
    
if __name__ == '__main__':

    f = open('conf.yml', 'r+')
    conf = yaml.load(f)

    USER = conf['userid']
    PASS = conf['password']
    PACTION = 'login'
    GAMES = conf['games']
    
    GAMENAME_QUERY = 'yourgamename'

    session = requests.session()

    login_info = {
            'pAction': PACTION,
            'username': USER,
            'password': PASS
            }


    url_login = 'http://www.boiteajeux.net/gestion.php'
    res = session.post(url_login, data=login_info)
    res.raise_for_status()

    gamedict = get_gameid(res.text, GAMENAME_QUERY)

    confdict = dict()
    for game in GAMES:
        confdict[game['id']]= game['name']

    diff_keys = gamedict.keys() - confdict.keys()

    gamelist = []
    for key in diff_keys:
        addgames={'id':key,'name':gamedict[key]}
        gamelist.append(addgames)
    if len(gamelist) > 0:
        f.write(yaml.dump(gamelist, default_flow_style=False))
    f.close()
