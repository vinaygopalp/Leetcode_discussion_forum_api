#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import threading
import time


def start_consumer():
    """Start the RabbitMQ consumer in a separate thread."""
    from django.core.management import call_command
    try:
        # Wait a bit for Django to fully initialize
        time.sleep(10)
        call_command('consume_queue')
    except Exception as e:
        print(f"Error starting consumer: {e}")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Leetcode.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Start consumer thread only when runserver is invoked
    if len(sys.argv) >= 2 and sys.argv[1] == "runserver":
        consumer_thread = threading.Thread(target=start_consumer, daemon=True)
        consumer_thread.start()
        print("Started RabbitMQ consumer thread")

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
