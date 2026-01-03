"""
Background Job Scheduler
Cron jobs for expiration updates, notifications, and analytics.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from app.workers.freshness_worker import update_all_freshness_status
from app.workers.notification_worker import send_morning_alerts, send_evening_reminders
from app.workers.analytics_worker import aggregate_weekly_analytics

scheduler = AsyncIOScheduler()


def start_scheduler():
    """Start the background job scheduler."""
    
    # Freshness Update - Daily at 12:01 AM
    scheduler.add_job(
        update_all_freshness_status,
        CronTrigger(hour=0, minute=1),
        id="freshness_update",
        name="Update Freshness Status",
        replace_existing=True,
    )
    
    # Morning Expiry Alerts - Daily at 7:00 AM
    scheduler.add_job(
        send_morning_alerts,
        CronTrigger(hour=7, minute=0),
        id="morning_alerts",
        name="Morning Expiry Alerts",
        replace_existing=True,
    )
    
    # Evening Reminders - Daily at 7:00 PM
    scheduler.add_job(
        send_evening_reminders,
        CronTrigger(hour=19, minute=0),
        id="evening_reminders",
        name="Evening Reminders",
        replace_existing=True,
    )
    
    # Weekly Analytics - Sundays at 11:00 PM
    scheduler.add_job(
        aggregate_weekly_analytics,
        CronTrigger(day_of_week="sun", hour=23, minute=0),
        id="weekly_analytics",
        name="Weekly Analytics Aggregation",
        replace_existing=True,
    )
    
    scheduler.start()
    print(f"📅 Scheduler started at {datetime.now()}")
    print(f"   Jobs scheduled: {len(scheduler.get_jobs())}")


def stop_scheduler():
    """Stop the background job scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        print("📅 Scheduler stopped")
