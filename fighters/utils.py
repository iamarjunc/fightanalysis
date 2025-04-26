def predict_fight_outcome(fighter1, fighter2):
    """
    Compare two fighters and predict the approximate fight outcome with more realistic logic.
    Returns a dictionary with predicted winner, confidence, scores, breakdown, and reason.
    """
    # Base weights for attributes
    weights = {
        'striking': 0.25,
        'grappling': 0.25,
        'stamina': 0.15,
        'defense': 0.15,
        'speed': 0.10,
        'recent_performance': 0.10
    }

    # Calculate base scores
    fighter1_score = (
        fighter1.striking * weights['striking'] +
        fighter1.grappling * weights['grappling'] +
        fighter1.stamina * weights['stamina'] +
        fighter1.defense * weights['defense'] +
        fighter1.speed * weights['speed']
    )
    fighter2_score = (
        fighter2.striking * weights['striking'] +
        fighter2.grappling * weights['grappling'] +
        fighter2.stamina * weights['stamina'] +
        fighter2.defense * weights['defense'] +
        fighter2.speed * weights['speed']
    )

    # Adjust for recent performance
    def get_recent_performance(fighter):
        fights = fighter.recent_fights.split('\n')[:3]
        wins = sum(1 for fight in fights if 'Win' in fight)
        return wins / max(len(fights), 1) * 100

    fighter1_recent = get_recent_performance(fighter1) * weights['recent_performance']
    fighter2_recent = get_recent_performance(fighter2) * weights['recent_performance']
    fighter1_score += fighter1_recent
    fighter2_score += fighter2_recent

    # Activity adjustment (penalize inactive fighters)
    activity_penalty = 10.0
    if not fighter1.is_active:
        fighter1_score -= activity_penalty
    if not fighter2.is_active:
        fighter2_score -= activity_penalty

    # Weight class impact (significant advantage for heavier fighter)
    weight_class_order = ['FLYWEIGHT', 'BANTAMWEIGHT', 'FEATHERWEIGHT', 'LIGHTWEIGHT', 
                         'WELTERWEIGHT', 'MIDDLEWEIGHT', 'LIGHT_HEAVYWEIGHT', 'HEAVYWEIGHT']
    f1_weight_index = weight_class_order.index(fighter1.weight_class) if fighter1.weight_class else -1
    f2_weight_index = weight_class_order.index(fighter2.weight_class) if fighter2.weight_class else -1

    weight_class_impact = 0
    weight_diff = 0
    if f1_weight_index != -1 and f2_weight_index != -1:
        weight_diff = abs(f1_weight_index - f2_weight_index)
        if weight_diff > 0:
            if f1_weight_index > f2_weight_index:
                weight_class_impact = 20.0 * weight_diff
                fighter1_score += weight_class_impact
                fighter2_score -= weight_class_impact * 0.5
            else:
                weight_class_impact = 20.0 * weight_diff
                fighter2_score += weight_class_impact
                fighter1_score -= weight_class_impact * 0.5

    # Size and knockout potential adjustment
    size_factor = 0.10 if max(f1_weight_index, f2_weight_index) >= 7 else 0.05
    knockout_factor = 0.15
    if f1_weight_index > f2_weight_index:
        fighter1_score += fighter1.striking * (size_factor + knockout_factor)
    elif f2_weight_index > f1_weight_index:
        fighter2_score += fighter2.striking * (size_factor + knockout_factor)

    # P4P ranking adjustment
    p4p_bonus = 5.0
    f1_p4p = fighter1.p4p_ranking if fighter1.p4p_ranking else float('inf')
    f2_p4p = fighter2.p4p_ranking if fighter2.p4p_ranking else float('inf')
    p4p_adjustment = 0
    if f1_p4p != float('inf') and f2_p4p != float('inf'):
        if f1_p4p < f2_p4p:
            p4p_adjustment = (f2_p4p - f1_p4p) * p4p_bonus
            fighter1_score += p4p_adjustment
        elif f2_p4p < f1_p4p:
            p4p_adjustment = (f1_p4p - f2_p4p) * p4p_bonus
            fighter2_score += p4p_adjustment

    # Martial art matchup adjustments
    martial_art_adjustments = {
        'MMA vs Kickboxing': {
            'grappling_bonus': 0.1,
            'striking_bonus': 0.1
        }
    }
    matchup_key = f"{fighter1.martial_art} vs {fighter2.martial_art}"
    if matchup_key in martial_art_adjustments:
        adjustments = martial_art_adjustments[matchup_key]
        fighter1_score += fighter1.grappling * adjustments['grappling_bonus']
        fighter2_score += fighter2.striking * adjustments['striking_bonus']

    # Fight context: Grappling more effective early, striking more effective if fight stays standing
    fight_context = 0.2
    context_adjustment_f1 = 0
    context_adjustment_f2 = 0
    if fighter1.grappling > fighter2.grappling + 10:
        context_adjustment_f1 = fighter1.grappling * fight_context
        fighter1_score += context_adjustment_f1
    if fighter2.striking > fighter1.striking + 10:
        context_adjustment_f2 = fighter2.striking * fight_context
        fighter2_score += context_adjustment_f2

    # Determine winner and confidence (amplify small differences)
    total_score = fighter1_score + fighter2_score
    if total_score == 0:
        return {
            'winner': 'Draw',
            'confidence': 50.0,
            'fighter1_score': 0,
            'fighter2_score': 0,
            'breakdown': 'No score calculated due to zero total.',
            'reason': 'No significant factors determined.'
        }

    score_diff = abs(fighter1_score - fighter2_score)
    amplification_factor = 1 + (score_diff / total_score) * 5
    fighter1_prob = (fighter1_score / total_score) * 100 * amplification_factor
    fighter2_prob = (fighter2_score / total_score) * 100 * amplification_factor
    total_prob = fighter1_prob + fighter2_prob
    fighter1_prob = (fighter1_prob / total_prob) * 100
    fighter2_prob = (fighter2_prob / total_prob) * 100

    if fighter1_score > fighter2_score:
        winner = fighter1.name
        confidence = fighter1_prob
    elif fighter2_score > fighter1_score:
        winner = fighter2.name
        confidence = fighter2_prob
    else:
        winner = 'Draw'
        confidence = 50.0

    # Determine reason for the win
    reason = "No clear reason identified."
    if fighter1_score > fighter2_score:
        if weight_class_impact > 10:
            reason = f"{fighter1.name}'s weight advantage overwhelmed {fighter2.name}."
        elif context_adjustment_f1 > 10:
            reason = f"{fighter1.name}'s grappling dominance controlled the fight against {fighter2.name}."
        elif fighter1.striking > fighter2.striking + 15:
            reason = f"{fighter1.name}'s striking outclassed {fighter2.name}'s defense."
        elif p4p_adjustment > 5:
            reason = f"{fighter1.name}'s higher ranking proved decisive over {fighter2.name}."
    elif fighter2_score > fighter1_score:
        if weight_class_impact > 10:
            reason = f"{fighter2.name}'s weight advantage overwhelmed {fighter1.name}."
        elif context_adjustment_f2 > 10:
            reason = f"{fighter2.name}'s striking power dominated {fighter1.name}."
        elif fighter2.striking > fighter1.striking + 15:
            reason = f"{fighter2.name}'s striking outclassed {fighter1.name}'s defense."
        elif p4p_adjustment > 5:
            reason = f"{fighter2.name}'s higher ranking proved decisive over {fighter1.name}."

    # Breakdown for transparency
    breakdown = (
        f"Base Scores: {fighter1.name}: {fighter1_score - fighter1_recent - weight_class_impact - context_adjustment_f1:.2f}, "
        f"{fighter2.name}: {fighter2_score - fighter2_recent - weight_class_impact - context_adjustment_f2:.2f}\n"
        f"Recent Performance Adjustment: {fighter1.name}: +{fighter1_recent:.2f}, "
        f"{fighter2.name}: +{fighter2_recent:.2f}\n"
        f"Activity Adjustment: {fighter1.name}: {'-10.0' if not fighter1.is_active else '0.0'}, "
        f"{fighter2.name}: {'-10.0' if not fighter2.is_active else '0.0'}\n"
        f"Weight Class Impact: Difference of {weight_diff} classes, "
        f"{fighter1.name}: {'+' if f1_weight_index > f2_weight_index else '-'}{weight_class_impact:.2f}, "
        f"{fighter2.name}: {'+' if f2_weight_index > f1_weight_index else '-'}{weight_class_impact:.2f}\n"
        f"Size/Knockout Adjustment: {fighter1.name}: +{(fighter1.striking * (size_factor + knockout_factor) if f1_weight_index > f2_weight_index else 0):.2f}, "
        f"{fighter2.name}: +{(fighter2.striking * (size_factor + knockout_factor) if f2_weight_index > f1_weight_index else 0):.2f}\n"
        f"P4P Ranking Adjustment: {fighter1.name}: +{(p4p_adjustment if f1_p4p < f2_p4p else 0):.2f}, "
        f"{fighter2.name}: +{(p4p_adjustment if f2_p4p < f1_p4p else 0):.2f}\n"
        f"Matchup Adjustment: {matchup_key} applied.\n"
        f"Context Adjustment: {fighter1.name}: +{context_adjustment_f1:.2f} (grappling), "
        f"{fighter2.name}: +{context_adjustment_f2:.2f} (striking)"
    )

    return {
        'winner': winner,
        'confidence': round(confidence, 2),
        'fighter1_score': round(fighter1_score, 2),
        'fighter2_score': round(fighter2_score, 2),
        'breakdown': breakdown,
        'reason': reason
    }