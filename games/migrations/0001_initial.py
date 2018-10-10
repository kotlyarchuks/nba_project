# Generated by Django 2.0.2 on 2018-10-09 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_created=True)),
                ('game', models.IntegerField()),
                ('author', models.CharField(max_length=50)),
                ('text', models.TextField()),
                ('likes', models.IntegerField(default=0)),
            ],
        ),
    ]