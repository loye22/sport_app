from celery import shared_task
from django.utils import timezone
from api.models import Event

@shared_task
def check_and_complete_events():
    now = timezone.now()
    # Get all events that are not completed
    events = Event.objects.exclude(status='Completed')
    for event in events:
        # Combine event date and end_time into a single datetime
        event_end = timezone.make_aware(
            timezone.datetime.combine(event.date, event.end_time)
        )
        if now >= event_end:
            event.status = 'Completed'
            event.save()
            print(f"Event '{event.title}' marked as Completed at {now}")
    return "Checked and updated events."