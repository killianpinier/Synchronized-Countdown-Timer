from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from .models import Session, Timer
import json
from .timer import SessionData, Response

import random
from datetime import datetime
from django.utils import timezone

def generate_session_id():
    id = 0
    for i in range(4):
        id *= 10
        id += random.randint(0, 9)
    return id

def index(request):
    if request.method == 'POST':
        print("post")
        if 'createSession' in request.POST:
            new_session = Session(session_id=generate_session_id())
            new_session.save()
            return redirect("session", session_id=new_session.session_id)
        if 'joinSession' in request.POST:
            session = get_object_or_404(Session, session_id=request.POST["sessionID"])
            return redirect("session", session_id=session.session_id)
    return render(request, "timer/index.html")

def session(request, session_id):
    session = Session.objects.get(session_id=session_id)
    if request.method == 'POST':
        duration = timezone.timedelta(hours=int(request.POST["hoursInput"]), minutes=int(request.POST["minutesInput"]), seconds=int(request.POST["secondsInput"]))
        new_timer = Timer(duration=duration, _session=session)
        new_timer.save()
        session.selected_timer = new_timer
        session.save()
    
    timers = Timer.objects.filter(_session=session)

    return render(request, "timer/session.html", {'session': session, "timers": timers})

def modify_selected_timer(request, session_id, timer_id):
    session = Session.objects.get(session_id=session_id)
    timer = Timer.objects.get(pk=timer_id)
    session.selected_timer = timer
    session.save()

    return redirect("session", session_id=session.session_id)

def get_timer_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_data = SessionData(data.get("timer_id"), data.get("status"))
            timer = Timer.objects.get(pk=session_data.current_timer)
            now = int(datetime.now().timestamp() * 1000)
            response = Response(
                timer.duration.seconds,
                timer.remaining.seconds,
                int(timer.end_at.timestamp() * 1000),
                timer.status,
                now,
            )
            return JsonResponse(response.to_map())
        except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    

def test(request):
    return render(request, "timer/test.html")