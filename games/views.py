from django.shortcuts import render
import requests
from django.utils import timezone

import urllib.request
import json

# https://stats.nba.com/stats/scoreboardv2?DayOffset=0&GameDate=2018-10-07&LeagueID=00


def nba_request(url):
    req_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'stats.nba.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    req = requests.get(url, headers=req_headers)
    if req.status_code == 200:
        return req.json()
    else:
        raise Exception('Something went wrong with request to NBA!')


def index(request):
    today = timezone.now() + timezone.timedelta(days=-1)
    today = today.strftime("%Y-%m-%d")
    url = f"https://stats.nba.com/stats/scoreboardv2?DayOffset=0&GameDate={today}&LeagueID=00"
    response = nba_request(url)
    games_list = [game[2] for game in response['resultSets'][0]['rowSet']]
    data = []
    for game in games_list:
        url = f"https://stats.nba.com/stats/boxscoresummaryv2?GameID={game}"
        response = nba_request(url)
        row = response['resultSets'][5]['rowSet']
        if row[0][-1] > row[1][-1]:
            winner = 'home'
        else:
            winner = 'away'
        data.append({
            'id': game,
            'home_team': row[0][5] + " " + row[0][6],
            'away_team': row[1][5] + " " + row[1][6],
            'home_team_score': row[0][-1],
            'away_team_score': row[1][-1],
            'winner': winner
        })

    return render(request, 'games/index.html', {'data': data})


def detail(request, game_id):
    # url = f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2018/scores/gamedetail/00{game_id}_gamedetail.json"
    # req_headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    #     'Accept-Encoding': 'gzip, deflate',
    #     'Accept-Language': 'en-US,en;q=0.8',
    #     'Connection': 'keep-alive',
    #     'Host': 'stats.nba.com',
    #     'Upgrade-Insecure-Requests': '1',
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    # }
    # req = requests.get(url, headers=req_headers)
    url = f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2018/scores/gamedetail/00{game_id}_gamedetail.json"
    with urllib.request.urlopen(url) as url_res:
        data = json.loads(url_res.read().decode())

    return render(request, 'games/detail.html', {'data': data})
