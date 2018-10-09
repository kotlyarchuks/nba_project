from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from .utils import api_request, today_games_list, get_json, get_boxscore, get_reddit_posts
from .forms import CommentForm
from .models import Comment


# https://stats.nba.com/stats/scoreboardv2?DayOffset=0&GameDate=2018-10-07&LeagueID=00


def index(request):
    data = today_games_list()
    posts = get_reddit_posts()

    return render(request, 'games/index.html', {'data': data, 'posts': posts})


def detail(request, game_id):
    data = get_boxscore(game_id)
    comments = Comment.objects.filter(game=game_id).order_by('-pub_date')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(game=game_id, author=form.cleaned_data.get('author'), text=form.cleaned_data.get('text'))
            comment.save()
            return HttpResponseRedirect(reverse('detail', args=[game_id]))
    else:
        form = CommentForm()

    return render(request, 'games/detail.html', {'data': data, 'form':form, 'comments': comments})
