from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Fighter
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .utils import predict_fight_outcome
from .models import Fighter, FightCard, Vote
from django.contrib import messages
from datetime import datetime

def fighter_list(request):
    fighters = Fighter.objects.all()
    weight_class = request.GET.get('weight_class', '')
    p4p_filter = request.GET.get('p4p_filter', '')

    if weight_class:
        fighters = fighters.filter(weight_class=weight_class)
    
    if p4p_filter == 'top_10':
        fighters = fighters.filter(p4p_ranking__isnull=False, p4p_ranking__lte=10).order_by('p4p_ranking')
    elif p4p_filter == 'top_5':
        fighters = fighters.filter(p4p_ranking__isnull=False, p4p_ranking__lte=5).order_by('p4p_ranking')
    elif p4p_filter == 'top_15':
        fighters = fighters.filter(p4p_ranking__isnull=False, p4p_ranking__lte=15).order_by('p4p_ranking')

    weight_classes = Fighter.WEIGHT_CLASSES
    context = {
        'fighters': fighters,
        'weight_classes': weight_classes,
        'selected_weight_class': weight_class,
        'selected_p4p_filter': p4p_filter,
    }
    return render(request, 'fighters/fighter_list.html', context)

def fighter_detail(request, pk):
    fighter = get_object_or_404(Fighter, pk=pk)
    return render(request, 'fighters/fighter_detail.html', {'fighter': fighter})

def search_fighters(request):
    query = request.GET.get('q', '')
    fighters = Fighter.objects.filter(
        Q(name__icontains=query) | Q(martial_art__icontains=query)
    )
    return render(request, 'fighters/search.html', {'fighters': fighters, 'query': query})

def compare_fighters(request):
    fighter1 = None
    fighter2 = None
    prediction = None
    breakdown = None
    error_message = None
    if request.method == 'POST':
        fighter1_id = request.POST.get('fighter1_id')
        fighter2_id = request.POST.get('fighter2_id')
        if fighter1_id and fighter2_id:
            try:
                fighter1 = Fighter.objects.get(id=fighter1_id)
                fighter2 = Fighter.objects.get(id=fighter2_id)
                if fighter1 == fighter2:
                    error_message = "Please select two different fighters."
                else:
                    prediction = predict_fight_outcome(fighter1, fighter2)
                    breakdown = prediction.get('breakdown', 'No breakdown available.')
            except Fighter.DoesNotExist:
                error_message = "One or both fighters could not be found. Please select valid fighters."
        else:
            error_message = "Please select two fighters to compare."
    return render(request, 'fighters/compare.html', {
        'fighter1': fighter1,
        'fighter2': fighter2,
        'prediction': prediction,
        'breakdown': breakdown,
        'error_message': error_message,
    })

@require_GET
def autocomplete(request):
    query = request.GET.get('q', '').lower()
    exclude_id = request.GET.get('exclude', '')
    if query:
        fighters = Fighter.objects.filter(name__icontains=query)
        if exclude_id and exclude_id.isdigit():
            fighters = fighters.exclude(id=int(exclude_id))
        fighters = fighters[:5]
        data = [{'id': fighter.id, 'name': fighter.name} for fighter in fighters]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

def countdown_view(request):
    upcoming_fights = FightCard.objects.filter(event_date__gte=datetime.now()).order_by('event_date')
    return render(request, 'fighters/countdown.html', {'upcoming_fights': upcoming_fights})

def poll_list_view(request):
    upcoming_fights = FightCard.objects.filter(event_date__gte=datetime.now()).order_by('event_date')
    return render(request, 'fighters/poll_list.html', {'upcoming_fights': upcoming_fights})



def poll_view(request, fight_id):
    try:
        fight_card = get_object_or_404(FightCard, id=fight_id)
        if not fight_card.fighter1 or not fight_card.fighter2:
            messages.error(request, "Fight card data is incomplete.")
            return redirect('fighters:poll_list')

        # Predict the winner based on stats if not already set
        if not fight_card.predicted_winner:
            total_stats_fighter1 = (fight_card.fighter1.striking + fight_card.fighter1.grappling + 
                                  fight_card.fighter1.stamina + fight_card.fighter1.defense + 
                                  fight_card.fighter1.speed)
            total_stats_fighter2 = (fight_card.fighter2.striking + fight_card.fighter2.grappling + 
                                  fight_card.fighter2.stamina + fight_card.fighter2.defense + 
                                  fight_card.fighter2.speed)
            fight_card.predicted_winner = fight_card.fighter1.name if total_stats_fighter1 > total_stats_fighter2 else fight_card.fighter2.name
            fight_card.save()

        # Handle voting
        if request.method == "POST":
            chosen_fighter_id = request.POST.get("chosen_fighter")
            session_key = f"voted_fight_{fight_id}"
            if request.session.get(session_key):
                messages.warning(request, "You have already voted for this fight!")
            elif chosen_fighter_id:
                try:
                    chosen_fighter = Fighter.objects.get(id=chosen_fighter_id)
                    Vote.objects.create(fight_card=fight_card, chosen_fighter=chosen_fighter)
                    request.session[session_key] = True
                    messages.success(request, "Thank you for voting!")
                except Fighter.DoesNotExist:
                    messages.error(request, "Invalid fighter selection.")
            else:
                messages.error(request, "Please select a fighter to vote for.")
            return redirect('fighters:poll', fight_id=fight_id)  # Fix: Use 'fight_id' instead of 'pk'

        # Calculate poll results
        votes_fighter1 = Vote.objects.filter(fight_card=fight_card, chosen_fighter=fight_card.fighter1).count()
        votes_fighter2 = Vote.objects.filter(fight_card=fight_card, chosen_fighter=fight_card.fighter2).count()
        total_votes = votes_fighter1 + votes_fighter2
        votes_fighter1_percent = (votes_fighter1 / total_votes * 100) if total_votes > 0 else 0
        votes_fighter2_percent = (votes_fighter2 / total_votes * 100) if total_votes > 0 else 0

        return render(request, 'fighters/poll.html', {
            'fight_card': fight_card,
            'votes_fighter1': votes_fighter1,
            'votes_fighter2': votes_fighter2,
            'votes_fighter1_percent': round(votes_fighter1_percent, 2),
            'votes_fighter2_percent': round(votes_fighter2_percent, 2),
        })
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('fighters:poll_list')