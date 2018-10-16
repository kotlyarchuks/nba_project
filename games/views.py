from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
import json
from django.core import serializers
from .utils import today_games_list, get_boxscore, get_reddit_posts, get_youtube_videos, get_standings, get_leaders
from .forms import CommentForm
from .models import Comment, Post, PostComment


# https://stats.nba.com/stats/scoreboardv2?DayOffset=0&GameDate=2018-10-07&LeagueID=00


def index(request):
    data = today_games_list()
    posts = Post.objects.all()
    videos = get_youtube_videos()
    standings = get_standings()
    leaders = get_leaders()

    return render(request, 'games/index.html', {
        'data': data,
        'posts': posts,
        'videos': videos,
        'standings': standings,
        'leaders': leaders
    })


@login_required
def detail(request, game_id):
    data = get_boxscore(game_id)
    comments = Comment.objects.filter(game=game_id).order_by('-pub_date')

    if request.is_ajax():
        text = request.POST.get('text')
        comment = Comment(game=game_id, author=request.user, text=text)
        comment.save()

        comments = Comment.objects.filter(game=game_id).order_by(
            '-pub_date').values('text', 'pub_date', 'author__username')
        comments = json.dumps(list(comments), indent=4,
                              sort_keys=True, default=str)
        context = {
            'comments': comments
        }
        return JsonResponse(context, safe=False)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(game=game_id, author=request.user,
                              text=form.cleaned_data.get('text'))
            comment.save()
            return HttpResponseRedirect(reverse('detail', args=[game_id]))
    else:
        form = CommentForm()

    return render(
        request,
        'games/detail.html',
        {'data': data, 'form': form, 'comments': comments}
    )
