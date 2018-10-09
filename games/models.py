from django.db import models
from django.utils import timezone

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
    pub_date = models.DateTimeField(default=timezone.now())
    author = models.CharField(max_length=50)
    text = models.TextField()
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.text