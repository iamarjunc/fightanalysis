# Generated by Django 5.2 on 2025-04-24 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fighters', '0003_remove_fighter_created_at_fighter_detailed_stats_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fighter',
            name='bio',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='fighter',
            name='defense',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='fighter',
            name='detailed_stats',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='fighter',
            name='grappling',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='fighter',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='fighters/'),
        ),
        migrations.AlterField(
            model_name='fighter',
            name='recent_fights',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='fighter',
            name='speed',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='fighter',
            name='stamina',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='fighter',
            name='striking',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='fighter',
            name='video_id',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
