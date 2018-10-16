from games.utils import get_reddit_posts
from games.models import Post, PostComment


def get_posts():
    Post.objects.all().delete()
    data = get_reddit_posts()
    for post in data:
        top_comment = PostComment(
            author=post['top_comment']['author'],
            text=post['top_comment']['text'],
            score=post['top_comment']['score']
        )
        top_comment.save()
        p = Post(
            title=post['title'],
            link=post['link'],
            url=post['url'],
            score=post['score'],
            comments=post['comments'],
            top_comment=PostComment.objects.get(pk=top_comment.id)
        )
        p.save()
