
from django.utils import timezone
from .models import Timer

# Timer Status
STOPPED = 0
RUNNING = 1
PAUSED  = 2

MILLISECONDS = 1000

class Response():
    def __init__(self, id, duration, remaining, end_at, status, timestamp):
        self.id = id
        self.duration = duration
        self.remaining = remaining
        self.end_at = end_at
        self.status = status
        self.timestamp = timestamp
    
    def to_map(self):
        return {
            "id": self.id,
            "duration": self.duration,
            "end_at": self.end_at,
            "status": self.status,
            "timestamp": self.timestamp,
            "remaining": self.remaining,
        }


def generate_response(timer, now):
    return Response(
        timer.id,
        timer.duration.seconds,
        timer.remaining.seconds,
        int(timer.end_at.timestamp() * 1000),
        timer.status,
        now,
    )

def update_timer(status_request, timer):
    now = timezone.now()
    match status_request:
        case 0: # REQUEST: Stop timer
            stop_timer(timer)
        case 1: # REQUEST: Start timer
            start_timer(timer, now)
        case 2: # REQUEST: Pause/Resume timer
            if timer.status == RUNNING:
                pause_timer(timer, now)
            elif timer.status == PAUSED:
                resume_timer(timer, now)
            else:
                raise ValueError("Request to pause/resume timer, but current status is Stopped")
        case _:
            # TODO : Return error to page
            print("Wrong status number")
    timer.save()

def stop_all_timer(session):
    timers = Timer.objects.filter(_session=session)
    for timer in timers:
        timer.status = 0
        timer.save() # Check if there is a way to save all at once after iteration

def change_selected_timer(session, timer_id):
    timer = Timer.objects.get(pk=timer_id)
    session.selected_timer = timer
    session.save()

def timer_end_at_field_check(timer, now):
    if timer.end_at.timestamp()*1000 - now < 0:
        timer.status = 0
        timer.save()

def stop_timer(timer):
    if timer.status == RUNNING or timer.status == PAUSED:
        timer.status = STOPPED
        timer.remaining = timer.duration
    else:
        raise ValueError("Request to stop timer but has already been Stopped.")

def start_timer(timer, now):
    if timer.status == STOPPED:
        timer.status = RUNNING
        timer.end_at = now + timer.duration
    else:
        raise ValueError("Request to start timer but has already been Started.")

def pause_timer(timer, now):
    timer.status = PAUSED
    timer.remaining = timezone.timedelta(seconds=timer.end_at.timestamp() - now.timestamp())

def resume_timer(timer, now):
    timer.status = RUNNING
    timer.end_at = now + timer.remaining