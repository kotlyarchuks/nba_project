from django.utils import timezone
import requests
import urllib.request
import json
import praw
from praw.models import MoreComments


def api_request(url):
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
    req.raise_for_status()
    if req.status_code == 200:
        return req.json()
    else:
        raise Exception('Something went wrong with request to NBA!')


def split_array(arr, size):
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
    arrs.append(arr)
    return arrs


def today_games_list():
    today = timezone.now() + timezone.timedelta(days=-2)
    today = today.strftime("%Y-%m-%d")
    url = "https://stats.nba.com/js/data/widgets/scores_leaders.json"
    response = api_request(url)['items'][0]['items'][0]
    arrs = split_array(response['playergametats'], 2)
    data = []
    for arr in arrs:
        data.append(
            {
                'id': arr[0]['GAME_ID'],
                'home_team': arr[1]['TEAM_CITY'] + " " + arr[1]['TEAM_NICKNAME'],
                'away_team': arr[0]['TEAM_CITY'] + " " + arr[0]['TEAM_NICKNAME'],
                'home_team_short': arr[1]['TEAM_ABBREVIATION'],
                'away_team_short': arr[0]['TEAM_ABBREVIATION'],
                'home_leaders': {
                    'pts': arr[1]['PTS_PLAYER_NAME'] + " - " + str(arr[1]['PTS']),
                    'reb': arr[1]['REB_PLAYER_NAME'] + " - " + str(arr[1]['REB']),
                    'ast': arr[1]['AST_PLAYER_NAME'] + " - " + str(arr[1]['AST'])
                },
                'away_leaders': {
                    'pts': arr[0]['PTS_PLAYER_NAME'] + " - " + str(arr[0]['PTS']),
                    'reb': arr[0]['REB_PLAYER_NAME'] + " - " + str(arr[0]['REB']),
                    'ast': arr[0]['AST_PLAYER_NAME'] + " - " + str(arr[0]['AST'])
                }
            }
        )

    # url = f"https://stats.nba.com/stats/scoreboardv2?DayOffset=0&GameDate={today}&LeagueID=00"
    # response = api_request(url)
    # games_list = [game[2] for game in response['resultSets'][0]['rowSet']]
    # if not games_list:
    #     return []
    # leaders_row = response['resultSets'][7]['rowSet']
    # leaders = []
    # arrs = split_array(leaders_row, 2)
    # for arr in arrs:
    #     leaders.append({
    #         'id': arr[0][0],
    #         'home_team_short': arr[1][4],
    #         'away_team_short': arr[0][4],
    #         'home_leaders': {
    #             'pts': arr[1][6] + " - " + str(arr[1][7]),
    #             'reb': arr[1][9] + " - " + str(arr[1][10]),
    #             'ast': arr[1][12] + " - " + str(arr[1][13])},
    #         'away_leaders': {
    #             'pts': arr[0][6] + " - " + str(arr[0][7]),
    #             'reb': arr[0][9] + " - " + str(arr[0][10]),
    #             'ast': arr[0][12] + " - " + str(arr[0][13])}
    #     })

    # scores = []
    # for game in games_list:
    #     url = f"https://stats.nba.com/stats/boxscoresummaryv2?GameID={game}"
    #     response = api_request(url)
    #     row = response['resultSets'][5]['rowSet']
    #     if row[0][-1] > row[1][-1]:
    #         winner = 'home'
    #     else:
    #         winner = 'away'
    #     scores.append({
    #         'id': game,
    #         'home_team': row[0][5] + " " + row[0][6],
    #         'away_team': row[1][5] + " " + row[1][6],
    #         'home_team_score': row[0][-1],
    #         'away_team_score': row[1][-1],
    #         'winner': winner,
    #     })

    # data = []
    # for score, leader in zip(scores, leaders):
    #     data.append({**score, **leader})

    return data


def get_json(url):
    with urllib.request.urlopen(url) as url_res:
        raw_data = json.loads(url_res.read().decode())
    return raw_data


def get_boxscore(game_id):
    raw_data = get_json(
        f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2018/scores/gamedetail/00{game_id}_gamedetail.json")['g']

    data = {
        'game_id': raw_data['gid'],
        'home_team': raw_data['hls']['tc'] + " " + raw_data['hls']['tn'],
        'home_team_short': raw_data['hls']['ta'],
        'away_team': raw_data['vls']['tc'] + " " + raw_data['vls']['tn'],
        'away_team_short': raw_data['vls']['ta'],
        'score': f"{raw_data['hls']['s']} - {raw_data['vls']['s']}",
        'home_fg': {
            'fga': raw_data['hls']['tstsg']['fga'],
            'fgm': raw_data['hls']['tstsg']['fgm'],
            'fgp': str(round((raw_data['hls']['tstsg']['fgm'] / raw_data['hls']['tstsg']['fga'])*100, 1)) + "%"
        },
        'away_fg': {
            'fga': raw_data['vls']['tstsg']['fga'],
            'fgm': raw_data['vls']['tstsg']['fgm'],
            'fgp': str(round((raw_data['vls']['tstsg']['fgm'] / raw_data['vls']['tstsg']['fga'])*100, 1)) + "%"
        },
        'home_3p': {
            '3pa': raw_data['hls']['tstsg']['tpa'],
            '3pm': raw_data['hls']['tstsg']['tpm'],
            '3pp': str(round((raw_data['hls']['tstsg']['tpm'] / raw_data['hls']['tstsg']['tpa'])*100, 1)) + "%"
        },
        'away_3p': {
            '3pa': raw_data['vls']['tstsg']['tpa'],
            '3pm': raw_data['vls']['tstsg']['tpm'],
            '3pp': str(round((raw_data['vls']['tstsg']['tpm'] / raw_data['vls']['tstsg']['tpa'])*100, 1)) + "%"
        },
        'home_players': raw_data['hls']['pstsg'],
        'away_players': raw_data['vls']['pstsg'],
    }
    return data


def get_reddit_posts():

    reddit = praw.Reddit(client_id='zzyGytCYBexyAw',
                         client_secret='CjlXDeEtCI_PPj2YQ-N8nPVylHQ',
                         user_agent='nba_project v1.0 by /u/kotlyarchuky',
                         username='kotlyarchuky',
                         password='Feralpower3634')
    nba = reddit.subreddit('nba')
    posts = nba.hot(limit=30)
    data = []
    for post in posts:
        post.comment_limit = 1
        index = 0
        top_comment = post.comments[index]
        while isinstance(top_comment, MoreComments):
            index += 1
            try:
                top_comment = post.comments[index]
            except Exception:
                pass
        data.append({
            'title': post.title,
            'text': post.selftext,
            'score': post.score,
            'url': post.url,
            'comments': post.num_comments,
            'link': post.permalink,
            'top_comment': {
                'author': top_comment.author,
                'text': top_comment.body,
                'score': top_comment.score
            }
        })
    return data
