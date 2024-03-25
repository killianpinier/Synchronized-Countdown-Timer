const TimerStatus = {
    STOPPED: 0,
    RUNNING: 1,
    PAUSED: 2,
};

const Action = {
    UPDATE: 0,
    MODIFY_SELECTED_TIMER: 1,
}

let timer_seconds = 0;
let timer_interval;

function updateTimerValue() {
    let timer_tag = document.getElementById('timer');
    let hours = String(Math.floor(timer_seconds / 3600)).padStart(2, '0');
    let minutes = String(Math.floor((timer_seconds % 3600) / 60)).padStart(2, '0');
    let remaining_seconds = String(timer_seconds % 60).padStart(2, '0');
    timer_tag.textContent = hours + ':' + minutes + ':' + remaining_seconds;
}

function updateTimer(end_at) {
    let milliseconds = end_at - new Date().getTime();
    if (Math.abs(milliseconds - Math.floor(milliseconds/1000)*1000) <= 100) {
        timer_seconds = Math.floor(milliseconds/1000);
    }

    if (timer_seconds < 300) {
        let timer_tag = document.getElementById('timer');
        timer_tag.style.color = "orange";
    }

    if (timer_seconds < 120) {
        let timer_tag = document.getElementById('timer');
        timer_tag.style.color = "red";
    }

    if (timer_seconds < 0) {
        clearInterval(timer_interval);

        const timer_element = document.getElementById('timer');
        const timer_id = timer_element.getAttribute('data-timer-id');
        const data = { action: Action.UPDATE, timer_id: timer_id, status: TimerStatus.STOPPED};
        socket.send(JSON.stringify(data));
        timer_seconds = response.duration;
        updateTimerValue();
        return;
    }
    updateTimerValue();
}

document.addEventListener('DOMContentLoaded', function() {
    const timer_element = document.getElementById('timer');
    const session_element = document.getElementById('session');
    const timer_id = timer_element.getAttribute('data-timer-id');
    const session_id = session_element.getAttribute('data-session-id');
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/timers/" + session_id + "/");

    socket.onmessage = async (event) => {
        const response = await JSON.parse(event.data);
        switch (response.status) {
            case TimerStatus.STOPPED:
                console.log("STOPPED");
                stop_timer(response);
                break;
            case TimerStatus.RUNNING:
                console.log("RUNNING");
                start_timer(response);
                break;
            case TimerStatus.PAUSED:
                pause_timer();
                console.log("PAUSED");
                break;
            default:
                console.log("default");
        }
    }

    sendAjaxRequest('/get_timer_info/', {timer_id: timer_id})
        .then(response => {
            switch (response['status']) {
                case TimerStatus.STOPPED: {
                    timer_seconds = response["duration"];
                    updateTimerValue();

                    document.getElementById('startTimerBtn').style.display = 'inline-block';
                    document.getElementById('pauseResumeTimerBtn').style.display = 'none';
                    document.getElementById('stopTimerBtn').style.display = 'none';
                    break;
                }
                case TimerStatus.RUNNING: {
                    timer_interval = setInterval(() => updateTimer(response["end_at"]), 100);
                
                    document.getElementById('startTimerBtn').style.display = 'none';
                    document.getElementById('pauseResumeTimerBtn').style.display = 'inline-block';
                    document.getElementById('pauseResumeTimerBtn').textContent = 'Pause';
                    document.getElementById('stopTimerBtn').style.display = 'inline-block';
                    break;
                }
                case TimerStatus.PAUSED: {
                    timer_seconds = response["remaining"];
                    updateTimerValue();

                    document.getElementById('startTimerBtn').style.display = 'none';
                    document.getElementById('pauseResumeTimerBtn').style.display = 'inline-block';
                    document.getElementById('pauseResumeTimerBtn').textContent = 'Resume';
                    document.getElementById('stopTimerBtn').style.display = 'inline-block';
                    break;
                }
            }
        })
        .catch(error => {
            console.error(error);
        })

    const startBtn = document.getElementById('startTimerBtn');
    startBtn.addEventListener('click', function() {
        const data = { action: Action.UPDATE, timer_id: timer_id, status: TimerStatus.RUNNING};
        socket.send(JSON.stringify(data));
    });

    const pauseResumeBtn = document.getElementById('pauseResumeTimerBtn');
    pauseResumeBtn.addEventListener('click', function() {
        if (timer_id) {
            const data = { action: Action.UPDATE, timer_id: timer_id, status: TimerStatus.PAUSED};
            socket.send(JSON.stringify(data));
        } else {
            console.error("Timer Id not found");
        }
    });

    const stopBtn = document.getElementById('stopTimerBtn');
    stopBtn.addEventListener('click', function() {
        if (timer_id) {
            const data = { action: Action.UPDATE, timer_id: timer_id, status: TimerStatus.STOPPED};
            socket.send(JSON.stringify(data));
        } else {
            console.error("Timer Id not found");
        }
    });














    // ---------
    function start_timer(response) {
        //timer_seconds = response.remaining;
        timer_interval = setInterval(() => updateTimer(response.end_at), 100);
        
        document.getElementById('startTimerBtn').style.display = 'none';
        document.getElementById('pauseResumeTimerBtn').style.display = 'inline-block';
        document.getElementById('pauseResumeTimerBtn').textContent = 'Pause';
        document.getElementById('stopTimerBtn').style.display = 'inline-block';
    }

    function pause_timer() {
        clearInterval(timer_interval);
        document.getElementById('pauseResumeTimerBtn').textContent = 'Resume';
    }

    function stop_timer(response) {
        clearInterval(timer_interval);
        timer_seconds = response.duration;
        updateTimerValue();

        document.getElementById('startTimerBtn').style.display = 'inline-block';
        document.getElementById('pauseResumeTimerBtn').style.display = 'none';
        document.getElementById('stopTimerBtn').style.display = 'none';
    }
});

function sendAjaxRequest(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    }).then(async response => {
        if (response.ok) {
            const data = await response.json();
            console.log(data);
            return data;
        } else {
            throw new Error('Error occured while updating timer status');
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}