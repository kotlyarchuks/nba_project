from django.shortcuts import render
from .utils import api_request, today_games_list, get_json, get_boxscore, get_reddit_posts


# https://stats.nba.com/stats/scoreboardv2?DayOffset=0&GameDate=2018-10-07&LeagueID=00


def index(request):
    data = today_games_list()
    posts = get_reddit_posts()

    return render(request, 'games/index.html', {'data': data, 'posts': posts})


def detail(request, game_id):
    data = get_boxscore(game_id)

    return render(request, 'games/detail.html', {'data': data})
