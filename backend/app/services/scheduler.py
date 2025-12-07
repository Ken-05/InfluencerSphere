"""
scheduler.py
------------
Manages periodic background tasks for the application, such as checking
alert thresholds and periodically updating metrics. This ensures crucial
business logic runs independently of user API requests.
"""
import threading
import time
from typing import Callable, Optional

from ..services.alert_service import get_alert_service, AlertService
from ..core.config import get_settings

# Global variable to manage the scheduler thread's state
stop_event: Optional[threading.Event] = None
scheduler_thread: Optional[threading.Thread] = None


class BackgroundScheduler:
    """
    Simulates a background scheduler to run periodic tasks like alert checking.
    Later: Use a APScheduler or Celery library.
    """

    def __init__(self, alert_service: AlertService):
        self.alert_service = alert_service
        self.interval = get_settings().ALERT_CHECK_INTERVAL_SECONDS
        print(f"INFO: Scheduler initialized. Alert check interval: {self.interval} seconds.")

    def _periodic_task(self):
        """The main loop that executes background jobs."""
        global stop_event

        while not stop_event.is_set():
            try:
                print("SCHEDULER: Starting periodic task execution...")

                # Execute the Alert Evaluation Logic
                triggered_alerts = self.alert_service.evaluate_all_alerts()

                if triggered_alerts:
                    print(f"SCHEDULER: Successfully triggered {len(triggered_alerts)} alerts!")
                    # Later: send to a notification queue (e.g., email, push)

                # Wait for the next interval or until the stop signal is received
                stop_event.wait(self.interval)

            except Exception as e:
                # Log the error but don't crash the thread
                print(f"SCHEDULER ERROR: An error occurred during task execution: {e}")
                time.sleep(self.interval)  # Wait before retrying

    def start(self):
        """Starts the background scheduler thread."""
        global stop_event, scheduler_thread

        if scheduler_thread and scheduler_thread.is_alive():
            print("WARNING: Scheduler is already running.")
            return

        print("SCHEDULER: Starting background thread.")
        stop_event = threading.Event()
        scheduler_thread = threading.Thread(target=self._periodic_task, daemon=True)
        scheduler_thread.start()

    def shutdown(self):
        """Signals the background scheduler thread to stop gracefully."""
        global stop_event, scheduler_thread

        if scheduler_thread and scheduler_thread.is_alive():
            print("SCHEDULER: Shutting down background thread...")
            stop_event.set()
            scheduler_thread.join(timeout=5)  # Wait up to 5 seconds for cleanup
            if scheduler_thread.is_alive():
                print("SCHEDULER WARNING: Thread did not stop gracefully.")
            else:
                print("SCHEDULER: Thread stopped successfully.")
        else:
            print("WARNING: Scheduler thread was not running.")


# Singleton instance of the scheduler
_scheduler_instance: Optional[BackgroundScheduler] = None


def get_scheduler() -> BackgroundScheduler:
    """Provides a singleton instance of the scheduler."""
    global _scheduler_instance
    if _scheduler_instance is None:
        # Resolve dependencies needed by the scheduler's tasks
        alert_service = get_alert_service()
        _scheduler_instance = BackgroundScheduler(alert_service=alert_service)
    return _scheduler_instance