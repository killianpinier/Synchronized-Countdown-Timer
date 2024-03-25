
from django.utils import timezone
from datetime import datetime

# Timer Status
STOPPED = 0
RUNNING = 1
PAUSED  = 2

MILLISECONDS = 1000


class SessionData():
    def __init__(self, current_timer, request_status):
        self.current_timer = current_timer
        self.request_status = request_status

class Response():
    def __init__(self, duration, remaining, end_at, status, timestamp):
        self.duration = duration
        self.remaining = remaining
        self.end_at = end_at
        self.status = status
        self.timestamp = timestamp
    
    def to_map(self):
        return {
            "duration": self.duration,
            "end_at": self.end_at,
            "status": self.status,
            "timestamp": self.timestamp,
            "remaining": self.remaining,
        }
    
    def update(self, timer, now):
        self.duration = timer.duration.seconds
        self.remaining = int(timer.remaining.total_seconds() * MILLISECONDS)
        self.end_at = int(timer.end_at.timestamp() * MILLISECONDS)
        self.status = timer.status
        self.timestamp = int(now.timestamp() * MILLISECONDS)




def update_timer(status_request, timer, response):
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

    response.update(timer, now)

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
        #timer.end_at = timezone.now() + timer.duration
    else:
        raise ValueError("Request to start timer but has already been Started.")

def pause_timer(timer, now):
    # TODO - Should we check if end_at > datetime.now() ?
    #now = datetime.now()
    #if timer.end_at.timestamp() > now.timestamp():
    timer.status = PAUSED
    timer.remaining = timezone.timedelta(seconds=timer.end_at.timestamp() - now.timestamp())
    #timer.remaining = timezone.timedelta(seconds=timer.end_at.timestamp() - now.timestamp())
    #else:
    #    raise ValueError("timer.end_at is less than datetimer.now()")

def resume_timer(timer, now):
    timer.status = RUNNING
    timer.end_at = now + timer.remaining
    #timer.end_at = timezone.now() + timer.remaining