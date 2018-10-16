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
    response = _get_json(url)['items'][0]['items'][0]
    arrs = _split_array(response['playergametats'], 2)
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
    return data


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
    pass


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
