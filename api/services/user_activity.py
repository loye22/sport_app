from django.db.models import Q, Count, Sum, F, Value, CharField
from django.db.models.functions import Concat
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from decimal import Decimal

from ..models import UserProfile, Event, EventStats, Category

def get_user_team(event, user_profile):
    """
    Returns the team letter (A-H) that the user belongs to in the given event,
    or None if not a member of any team.
    """
    for letter in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
        field = getattr(event, f'team_{letter}_members')
        if user_profile in field.all():  # field.all() is cached if prefetched
            return letter.upper()
    return None

def get_participated_events(user_profile, completed_only=False):
    """
    Returns a QuerySet of events where the user is a member of any team.
    Optionally filter by status='Completed'.
    """
    q = Q(team_a_members=user_profile) | Q(team_b_members=user_profile) | \
        Q(team_c_members=user_profile) | Q(team_d_members=user_profile) | \
        Q(team_e_members=user_profile) | Q(team_f_members=user_profile) | \
        Q(team_g_members=user_profile) | Q(team_h_members=user_profile)
    events = Event.objects.filter(q)
    if completed_only:
        events = events.filter(status='Completed')
    return events

def get_organized_events(user_profile):
    """Returns all events hosted by the user."""
    return Event.objects.filter(host=user_profile)

def get_actual_members(event):
    """
    Returns the number of distinct users that are in any team of the event.
    Assumes that the event's team_members have been prefetched.
    """
    members = set()
    for letter in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
        field = getattr(event, f'team_{letter}_members')
        members.update(field.all())  # field.all() works if prefetched
    return len(members)


def get_user_activity_summary(user_profile, request=None):
    """
    Computes the full activity summary for a given UserProfile.
    Returns a dict with keys: activityOverview, atAGlance, topActivities,
    activityPatterns, statistics, bestAttendance.
    """
    # 1. Fetch all events the user has participated in (any status)
    participated_events = get_participated_events(user_profile)
    # Prefetch related team members, stats, and category to avoid N+1
    participated_events = participated_events.select_related('stats', 'category', 'host') \
        .prefetch_related(
            'team_a_members', 'team_b_members', 'team_c_members',
            'team_d_members', 'team_e_members', 'team_f_members',
            'team_g_members', 'team_h_members'
        )

    # 2. Filter completed events for win/loss calculations
    completed_events = [e for e in participated_events if e.status == 'Completed']

    # 3. Compute matches, wins, losses for overview
    matches = 0
    wins = 0
    losses = 0
    for event in completed_events:
        stats = getattr(event, 'stats', None)
        if stats and stats.team_winner != 'ND':
            user_team = get_user_team(event, user_profile)
            if user_team:
                matches += 1
                if stats.team_winner == user_team:
                    wins += 1
                else:
                    losses += 1

    win_rate = f"{int((wins / matches) * 100) if matches > 0 else 0}%"

    # 4. atAGlance
    total_joined = participated_events.count()
    total_organized = get_organized_events(user_profile).count()
    # Hours active: sum of event durations (end_time - start_time) for completed events (or all)
    # We'll use completed events for consistency; you can change to all if needed.
    hours_active_seconds = 0
    for event in completed_events:
        if event.start_time and event.end_time:
            start = timezone.datetime.combine(event.date, event.start_time)
            end = timezone.datetime.combine(event.date, event.end_time)
            hours_active_seconds += (end - start).total_seconds()
    hours_active = f"{int(hours_active_seconds / 3600)}h" if hours_active_seconds > 0 else "0h"

    # Average attendance (based on all participated events)
    attendance_percentages = []
    for event in participated_events:
        if event.max_members > 0:
            actual = get_actual_members(event)
            pct = (actual / event.max_members) * 100
            attendance_percentages.append(pct)
    avg_attendance = f"{int(sum(attendance_percentages) / len(attendance_percentages))}%" if attendance_percentages else "0%"

    # 5. topActivities – group by event title (you could also group by category)
    groups = defaultdict(lambda: {
        'events': [],
        'wins': 0,
        'losses': 0
    })
    for event in completed_events:  # We only care about completed for win/loss stats
        title = event.title
        groups[title]['events'].append(event)
        user_team = get_user_team(event, user_profile)
        stats = getattr(event, 'stats', None)
        if stats and stats.team_winner != 'ND' and user_team:
            if stats.team_winner == user_team:
                groups[title]['wins'] += 1
            else:
                groups[title]['losses'] += 1

    top_activities = []
    for title, data in groups.items():
        event_list = data['events']
        first = event_list[0]
        # Determine scoring: if any event in group has a non-empty score, consider "Scored"
        scoring = "Scored" if any(e.score for e in event_list) else "No Scored"
        # For fitness or custom, you might add more logic; for now we use category name as type
        # You can map category.name to a type if needed, e.g., "Wellness", "Team Activity"
        # For simplicity, we use category.name
        category_name = first.category.name if first.category else "General"
        # Date range
        dates = [e.date for e in event_list]
        min_date = min(dates)
        max_date = max(dates)
        date_range = f"{min_date.strftime('%b')} - {max_date.strftime('%b %Y')}" if min_date != max_date else min_date.strftime('%b %Y')
        # For non-scored activities, we might not have win/lose; we'll still include played
        played = len(event_list)
        win = data['wins']
        lose = data['losses']
        win_rate_act = f"{int((win / played) * 100) if played > 0 else 0}%"
        
        # Category image
        category_image = ""
        if first.category and first.category.image:
            if request:
                category_image = request.build_absolute_uri(first.category.image.url)
            else:
                category_image = first.category.image.url

        # Build entry
        entry = {
            'name': title,
            'type': category_name,
            'scoring': scoring,
            'played': played,
            'dateRange': date_range,
            'win': win,
            'lose': lose,
            'winRate': win_rate_act,
            'categoryImage': category_image,
            'category_image': category_image,
            'image': category_image,
        }
        top_activities.append(entry)

    # 6. activityPatterns
    category_counts = {}
    for event in participated_events:
        cat = event.category.name if event.category else None
        if cat:
            category_counts[cat] = category_counts.get(cat, 0) + 1
    most_active_category = max(category_counts, key=category_counts.get) if category_counts else None
    total = len(participated_events)
    avg_pct = f"{int((category_counts.get(most_active_category, 0) / total) * 100) if total > 0 else 0}%"

    # Longest streak in weeks (based on event dates)
    dates = sorted(set(event.date for event in participated_events))
    max_streak = 0
    current_streak = 0
    # We'll consider consecutive weeks: difference <= 7 days
    for i, d in enumerate(dates):
        if i == 0:
            current_streak = 1
        else:
            delta = (d - dates[i-1]).days
            if delta <= 7:
                current_streak += 1
            else:
                max_streak = max(max_streak, current_streak)
                current_streak = 1
    max_streak = max(max_streak, current_streak) if dates else 0
    longest_streak = f"{max_streak} Weeks" if max_streak > 0 else "0 Weeks"

    # 7. statistics – list of the last 10 unique categories (without repeat)
    statistics_list = []
    last_categories = []
    seen_category_ids = set()
    
    # Sort participated events in Python to avoid another database query
    sorted_events = sorted(participated_events, key=lambda e: (e.date, e.start_time), reverse=True)
    
    for event in sorted_events:
        if event.category:
            if event.category.id not in seen_category_ids:
                seen_category_ids.add(event.category.id)
                last_categories.append(event.category)
                if len(last_categories) == 10:
                    break

    for cat_obj in last_categories:
        # Filter completed events in that category
        cat_events = [e for e in completed_events if e.category and e.category.id == cat_obj.id]
        stat_match = len(cat_events)
        stat_win = 0
        stat_lost = 0
        for e in cat_events:
            user_team = get_user_team(e, user_profile)
            stats = getattr(e, 'stats', None)
            if stats and stats.team_winner != 'ND' and user_team:
                if stats.team_winner == user_team:
                    stat_win += 1
                else:
                    stat_lost += 1
        
        stat_img = ""
        if cat_obj.image:
            if request:
                stat_img = request.build_absolute_uri(cat_obj.image.url)
            else:
                stat_img = cat_obj.image.url

        statistics_list.append({
            'sport': cat_obj.name,
            'win': stat_win,
            'lost': stat_lost,
            'match': stat_match,
            'img': stat_img,
        })

    # 8. bestAttendance
    best_att = None
    best_pct = 0
    for event in participated_events:
        if event.max_members > 0:
            actual = get_actual_members(event)
            pct = (actual / event.max_members) * 100
            if pct > best_pct:
                best_pct = pct
                best_att = {
                    'activity': event.title,
                    'average': f"{int(best_pct)}%",
                    'breakdown': f"{int(best_pct)}% / 100%"
                }

    # Build final dict
    return {
        'activityOverview': {
            'matches': matches,
            'win': wins,
            'loses': losses,
            'winRate': win_rate,
        },
        'atAGlance': {
            'activitiesJoined': total_joined,
            'activitiesOrganized': total_organized,
            'hoursActive': hours_active,
            'averageAttendance': avg_attendance,
        },
        'topActivities': top_activities,
        'activityPatterns': {
            'mostActiveCategory': most_active_category or "None",
            'averagePercentage': avg_pct,
            'longestStreak': longest_streak,
        },
        'statistics': statistics_list,
        'bestAttendance': best_att or {
            'activity': 'N/A',
            'average': '0%',
            'breakdown': '0% / 100%'
        }
    }
