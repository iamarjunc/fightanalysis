
from django.contrib import admin
from .models import FightCard, Fighter, Vote

@admin.register(Fighter)
class FighterAdmin(admin.ModelAdmin):
    list_display = ('name', 'martial_art', 'record', 'weight_class', 'p4p_ranking', 'is_active')  # Added new fields
    list_filter = ('weight_class', 'is_active')  # Filter by weight class and active status
    fields = ('name', 'martial_art', 'record', 'weight_class', 'p4p_ranking', 'strengths', 'weaknesses', 'bio', 'photo', 'striking', 'grappling', 'stamina', 'defense', 'speed', 'video_id', 'detailed_stats', 'recent_fights', 'is_active')
    ordering = ('p4p_ranking',)  # Sort by P4P ranking by default
    
    
admin.site.register(FightCard)
admin.site.register(Vote)