import time

def long_task(callback=None):
    """Simulated long task. Calls `callback(progress)` each step."""
    total_steps = 10
    for i in range(total_steps):
        time.sleep(0.5)  # simulate work
        progress = (i + 1) / total_steps * 100
        if callback:
            callback(progress)
    return "Task Complete"
