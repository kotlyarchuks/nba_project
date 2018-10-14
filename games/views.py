from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
import json
from django.core import serializers
from .utils import api_request, today_games_list, get_json, get_boxscore, get_reddit_posts
from .forms import CommentForm
from .models import Comment, Post, PostComment


# https://stats.nba.com/stats/scoreboardv2?DayOffset=0&GameDate=2018-10-07&LeagueID=00


def index(request):
    data = today_games_list()
    posts = Post.objects.all()

    return render(request, 'games/index.html', {'data': data, 'posts': posts})


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
        # comments = serializers.serialize('json', comments)
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
