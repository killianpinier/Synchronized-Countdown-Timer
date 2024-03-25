const TimerStatus = {
    STOPPED: 0,
    RUNNING: 1,
    PAUSED: 2,
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
    if (timer_seconds < 0) {
        clearInterval(timer_interval);

        const timerElement = document.getElementById('timer');
        const timerId = timerElement.getAttribute('data-timer-id');
        sendAjaxRequest('/update_session/', {timer_id: timerId, status: TimerStatus.STOPPED})
            .then(response => {
                timer_seconds = response['duration'];
                updateTimerValue();
            })
            .catch(error => {
                console.error("Error", error);
            });
        return;
    }
    updateTimerValue();
}

document.addEventListener('DOMContentLoaded', function() {
    const timerElement = document.getElementById('timer');
    const timerId = timerElement.getAttribute('data-timer-id');
    sendAjaxRequest('/get_timer_info/', {timer_id: timerId})
        .then(response => {
            if (response['status'] == TimerStatus.RUNNING) {
                timer_interval = setInterval(() => updateTimer(response["end_at"]), 100);
                
                document.getElementById('startTimerBtn').style.display = 'none';
                document.getElementById('pauseResumeTimerBtn').style.display = 'inline-block';
                document.getElementById('pauseResumeTimerBtn').textContent = 'Pause';
                document.getElementById('stopTimerBtn').style.display = 'inline-block';

            } else if (response['status'] == TimerStatus.PAUSED) {
                timer_seconds = response["remaining"];
                updateTimerValue();

                document.getElementById('startTimerBtn').style.display = 'none';
                document.getElementById('pauseResumeTimerBtn').style.display = 'inline-block';
                document.getElementById('pauseResumeTimerBtn').textContent = 'Resume';
                document.getElementById('stopTimerBtn').style.display = 'inline-block';
            } else{
                timer_seconds = response["duration"];
                updateTimerValue();

                document.getElementById('startTimerBtn').style.display = 'inline-block';
                document.getElementById('pauseResumeTimerBtn').style.display = 'none';
                document.getElementById('stopTimerBtn').style.display = 'none';
            }
        })
        .catch(error => {
            console.error(error);
        })

    const startBtn = document.getElementById('startTimerBtn');
    startBtn.addEventListener('click', function() {
        if (timerId) {
            const url = '/update_session/';
            const data = { timer_id: timerId, status: TimerStatus.RUNNING};
            sendAjaxRequest(url, data)
                .then(response => {
                    timer_seconds = response["duration"];
                    timer_interval = setInterval(() => updateTimer(response["end_at"]), 100);
                    
                    document.getElementById('startTimerBtn').style.display = 'none';
                    document.getElementById('pauseResumeTimerBtn').style.display = 'inline-block';
                    document.getElementById('pauseResumeTimerBtn').textContent = 'Pause';
                    document.getElementById('stopTimerBtn').style.display = 'inline-block';

                })
                .catch(error => {
                    console.error('Error', error);
                })

        } else {
            console.error("Timer Id not found");
        }
    });

    const pauseResumeBtn = document.getElementById('pauseResumeTimerBtn');
    pauseResumeBtn.addEventListener('click', function() {
        if (timerId) {
            const url = '/update_session/';
            const data = { timer_id: timerId, status: TimerStatus.PAUSED};
            sendAjaxRequest(url, data)
                .then(response => {
                    if (response["status"] == TimerStatus.PAUSED) {
                        clearInterval(timer_interval);
                        document.getElementById('pauseResumeTimerBtn').textContent = 'Resume';
                    } else {
                        timer_seconds = Math.floor(response["remaining"]/1000);
                        timer_interval = setInterval(() => updateTimer(response["end_at"]), 100);
                        document.getElementById('pauseResumeTimerBtn').textContent = 'Pause';
                    }
                })
                .catch(error => {
                    console.error(error);
                })
        } else {
            console.error("Timer Id not found");
        }
    });

    const stopBtn = document.getElementById('stopTimerBtn');
    stopBtn.addEventListener('click', function() {
        if (timerId) {
            const url = '/update_session/';
            const data = { timer_id: timerId, status: TimerStatus.STOPPED};
            sendAjaxRequest(url, data)
                .then(response => {
                    clearInterval(timer_interval);
                    timer_seconds = response["duration"];
                    updateTimerValue();

                    document.getElementById('startTimerBtn').style.display = 'inline-block';
                    document.getElementById('pauseResumeTimerBtn').style.display = 'none';
                    document.getElementById('stopTimerBtn').style.display = 'none';
                })
                .catch(error => {
                    console.error(error);
                });
        } else {
            console.error("Timer Id not found");
        }
    });
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