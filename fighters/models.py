from django.db import models
import json

class Fighter(models.Model):
    # Weight class choices (common UFC weight classes)
    WEIGHT_CLASSES = (
        ('FLYWEIGHT', 'Flyweight (125 lbs)'),
        ('BANTAMWEIGHT', 'Bantamweight (135 lbs)'),
        ('FEATHERWEIGHT', 'Featherweight (145 lbs)'),
        ('LIGHTWEIGHT', 'Lightweight (155 lbs)'),
        ('WELTERWEIGHT', 'Welterweight (170 lbs)'),
        ('MIDDLEWEIGHT', 'Middleweight (185 lbs)'),
        ('LIGHT_HEAVYWEIGHT', 'Light Heavyweight (205 lbs)'),
        ('HEAVYWEIGHT', 'Heavyweight (265 lbs)'),
    )

    name = models.CharField(max_length=100)
    martial_art = models.CharField(max_length=50)
    record = models.CharField(max_length=20)
    strengths = models.TextField()
    weaknesses = models.TextField()
    bio = models.TextField()
    photo = models.ImageField(upload_to='fighters/', blank=True, null=True)
    striking = models.IntegerField()
    grappling = models.IntegerField()
    stamina = models.IntegerField()
    defense = models.IntegerField()
    speed = models.IntegerField()
    video_id = models.CharField(max_length=50, blank=True)
    detailed_stats = models.JSONField(default=dict)
    recent_fights = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    weight_class = models.CharField(max_length=20, choices=WEIGHT_CLASSES, blank=True)
    p4p_ranking = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_detailed_stats(self):
        try:
            return self.detailed_stats if isinstance(self.detailed_stats, dict) else json.loads(self.detailed_stats)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_recent_fights(self):
        return self.recent_fights.splitlines() if self.recent_fights else []

class FightCard(models.Model):
    fighter1 = models.ForeignKey(Fighter, related_name='fightcard_fighter1', on_delete=models.CASCADE)
    fighter2 = models.ForeignKey(Fighter, related_name='fightcard_fighter2', on_delete=models.CASCADE)
    event_name = models.CharField(max_length=100)
    event_date = models.DateTimeField()
    predicted_winner = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.event_name}: {self.fighter1.name} vs {self.fighter2.name}"

class Vote(models.Model):
    fight_card = models.ForeignKey(FightCard, related_name='votes', on_delete=models.CASCADE)
    chosen_fighter = models.ForeignKey(Fighter, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)  # Automatically set when vote is created

    def __str__(self):
        return f"Vote for {self.chosen_fighter} in {self.fight_card}"