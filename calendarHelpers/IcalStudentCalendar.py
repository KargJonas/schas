from datetime import datetime
from typing import Dict, List

import icalendar


class IcalStudentCalendar:
    def __init__(self, ical_content):
        self.events = self.extractEvents(ical_content)

    def getEventsForDay(self, date: datetime):
        if date.date() not in self.events:
            return []
        return sorted(self.events[date.date()], key=lambda event: event.startTime)

    @staticmethod
    def extractEvents(content) -> Dict[datetime, List]:
        cal = icalendar.Calendar.from_ical(content)
        events: Dict[datetime, List] = {event.start.date(): [] for event in cal.walk("VEVENT")}
        for event in cal.walk("VEVENT"):
            startDay: datetime = event.start.date()
            events[startDay].append(Event(event))
        return events


class Event:
    def __init__(self, event: icalendar.Event):
        summary: str = event.get('summary', '')
        self.isTest = summary.startswith('LVA-Prüfung')
        if self.isTest:
            summary = summary[summary.index("/") + 2:]
        parts = str(summary).split(" / ")
        self.title = parts[0]
        self.lecturer = parts[1]
        self.lvaNumber = parts[2]
        self.startTime = event.start
        self.room = str(event.get('location'))
