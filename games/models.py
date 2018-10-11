from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# class Game(models.Model):
#     date = models.DateTimeField()
#     home_team = models.CharField(max_length=200)
#     away_team = models.CharField(max_length=200)
#     home_score = models.IntegerField()
#     away_score = models.IntegerField()

#     def __str__(self):
#         return f"{self.home_team} {self.home_score} - {self.away_score} {self.away_team}"


class Comment(models.Model):
    game = models.IntegerField()
    pub_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField('Your comment')
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.text


class PostComment(models.Model):
    author = models.CharField(max_length=100)
    text = models.TextField()
    score = models.IntegerField()


class Post(models.Model):
    title = models.CharField(max_length=250)
    link = models.CharField(max_length=250)
    url = models.CharField(max_length=250)
    score = models.IntegerField()
    comments = models.IntegerField()
    top_comment = models.ForeignKey(PostComment, on_delete=models.CASCADE)



