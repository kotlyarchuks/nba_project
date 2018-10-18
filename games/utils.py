from django.utils import timezone
import requests
import urllib.request
import json
import praw
from praw.models import MoreComments
from .teams import TEAMS


def _get_json(url):
    with urllib.request.urlopen(url) as url_res:
        raw_data = json.loads(url_res.read().decode())
    return raw_data


def _split_array(arr, size):
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
    raw_data = _get_json(url)['items'][0]['items'][0]
    arrs = _split_array(raw_data['playergametats'], 2)
    leaders = []
    for arr in arrs:
        leaders.append(
            {
                'id': arr[0]['GAME_ID'],
                'leaders': [
                    {
                        'team_abbr': arr[1]['TEAM_ABBREVIATION'],
                        'pts': arr[1]['PTS_PLAYER_NAME'] + " - " + str(arr[1]['PTS']),
                        'reb': arr[1]['REB_PLAYER_NAME'] + " - " + str(arr[1]['REB']),
                        'ast': arr[1]['AST_PLAYER_NAME'] + " - " + str(arr[1]['AST'])
                    },
                    {
                        'team_abbr': arr[0]['TEAM_ABBREVIATION'],
                        'pts': arr[0]['PTS_PLAYER_NAME'] + " - " + str(arr[0]['PTS']),
                        'reb': arr[0]['REB_PLAYER_NAME'] + " - " + str(arr[0]['REB']),
                        'ast': arr[0]['AST_PLAYER_NAME'] + " - " + str(arr[0]['AST'])
                    }
                ]
            }
        )

    url = "https://data.nba.com/data/5s/v2015/json/mobile_teams/nba/2018/scores/00_todays_scores.json"
    raw_data = _get_json(url)['gs']['g']
    scores = []
    for game in raw_data:
        if game['v']['s'] > game['h']['s']:
            winner = 'away'
        else:
            winner = 'home'
        scores.append({
            'id': game['gid'],
            'home_team': game['h']['tc'] + " " + game['h']['tn'],
            'home_team_short': game['h']['ta'],
            'home_score': game['h']['s'],
            'away_team': game['v']['tc'] + " " + game['v']['tn'],
            'away_team_short': game['v']['ta'],
            'away_score': game['v']['s'],
            'winner': winner
        })
    for game in leaders:
        for score in scores:
            if score['id'] == game['id']:
                for leader in game['leaders']:
                    if leader['team_abbr'] == score['home_team_short']:
                        game['home_leaders'] = leader
                    else:
                        game['away_leaders'] = leader
                game['away_score'] = score['away_score']
                game['away_team'] = score['away_team']
                game['away_team_short'] = score['away_team_short']
                game['home_score'] = score['home_score']
                game['home_team'] = score['home_team']
                game['home_team_short'] = score['home_team_short']
                game['winner'] = score['winner']
                break

    return leaders


def get_boxscore(game_id):
    url = f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2018/scores/gamedetail/00{game_id}_gamedetail.json"
    raw_data = _get_json(url)['g']

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


def get_standings():
    url = "https://data.nba.net/prod/v2/current/standings_conference.json"
    raw_data = _get_json(url)['league']['standard']['conference']
    data = {
        'east': [],
        'west': []
    }
    for team in raw_data['east']:
        data['east'].append({
            'team': TEAMS[team['teamId']],
            'win': team['win'],
            'loss': team['loss']
        })
    for team in raw_data['west']:
        data['west'].append({
            'team': TEAMS[team['teamId']],
            'win': team['win'],
            'loss': team['loss']
        })
    return data


def get_leaders():
    url = "https://stats.nba.com/js/data/widgets/home_season.json"
    raw_data = _get_json(url)['items'][0]['items']
    data = {
        'pts': [],
        'reb': [],
        'ast': []
    }
    for row in raw_data[0]['playerstats'][:5]:
        data['pts'].append({
            'player': row['PLAYER_NAME'],
            'num': row['PTS']
        })
    for row in raw_data[1]['playerstats'][:5]:
        data['reb'].append({
            'player': row['PLAYER_NAME'],
            'num': row['REB']
        })
    for row in raw_data[2]['playerstats'][:5]:
        data['ast'].append({
            'player': row['PLAYER_NAME'],
            'num': row['AST']
        })
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


def get_youtube_videos():
    videos = []
    url = "https://www.googleapis.com/youtube/v3/search?channelId=UCWJ2lWNubArHWmf3FIHbfcQ&maxResults=20&order=date&part=snippet&key=AIzaSyA1p0Gsy_cSIF6BVz9qpTWy9law8Z9_FBA"
    req = requests.get(url)
    req.raise_for_status()
    res = req.json()['items']
    for video in res:
        videos.append({
            'id': video['id']['videoId'],
            'title': video['snippet']['title'],
            'thumbnail': video['snippet']['thumbnails']['medium']['url']
        })
    return videos


def get_recap(q):
    url = f"https://www.googleapis.com/youtube/v3/search?channelId=UCoh_z6QB0AGB1oxWufvbDUg&maxResults=1&order=date&part=snippet&key=AIzaSyA1p0Gsy_cSIF6BVz9qpTWy9law8Z9_FBA&q={q}"
    req = requests.get(url)
    req.raise_for_status()
    res = req.json()['items'][0]
    return {
        'id': res['id']['videoId'],
        'title': res['snippet']['title'],
        'thumbnail': res['snippet']['thumbnails']['medium']['url']
    }
