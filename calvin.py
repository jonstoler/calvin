#!/usr/bin/env python3

import sys
import os.path
from datetime import date, timedelta
from dateutil.rrule import rrule, DAILY, MONTHLY
import calendar

class Category:
    def __init__(self, name):
        self.items = []
        self.subcategories = []
        if name[-1] == ':':
            name = name[:-2]
        self.name = name
        self.parent = None

    def add_subcategory(self, name):
        if self.parent:
            return self.parent.add_subcategory(name)
        else:
            if name[:-2] == '::':
                name = name[:-3]
            c = Category(name[1:])
            c.parent = self
            self.subcategories.append(c)
            return c

    def add_item(self, item):
        self.items.append(item)

class Event:
    def __init__(self, string):
        self.year = None
        self.month = None
        self.day = None
        self.offset = None
        self.start_time = None
        self.end_time = None
        self.start_repeat = None
        self.end_repeat = None
        self.description = None
        self.location = None

        components = string.split(' ')
        if components[3][0] == '+' or components[3][0] == '-':
            date = self.parse_date(' '.join(components[:4]))
            current = 4
        else:
            date = self.parse_date(' '.join(components[:3]))
            current = 3
        self.year = date['year']
        self.month = date['month']
        self.day = date['day']
        self.offset = date['offset']

        if '-' in components[current]:
            spl = components[current].split('-')
            self.start_time = spl[0]
            self.end_time = spl[1]
        else:
            self.start_time = components[current]
        current += 1

        if components[current] == '~':
            current += 1
            date = self.parse_date(' '.join(components[current:current+3]), False)
            current += 3
            self.start_repeat = date

        if components[current] == '->':
            current += 1
            date = self.parse_date(' '.join(components[current:current+3]), False)
            current += 3
            self.end_repeat = date

        current += 1
        desc = ' '.join(components[current:])

        if '@' in desc:
            spl = desc.split(' @ ')
            self.description = spl[0]
            self.location = spl[1]
        else:
            self.description = desc

    def parse_date(self, date, globs_allowed=True):
        components = date.split(' ')
        year = components[0]
        if year == '*':
            year = -1
        else:
            year = int(year)

        month = components[1].lower()
        if month == '*':
            month = -1
        else:
            for i in range(1, 13):
                if calendar.month_abbr[i].lower() == month:
                    month = i
                    break
            if type(month) == str:
                # error
                pass

        day = components[2].lower()
        if day == '*':
            day = -1
        elif day.isdigit():
            day = int(day)

        offset = 0
        if len(components) > 3:
            offset = int(components[3])

        return {'year': year, 'month': month, 'day': day, 'offset': offset}
    
    def generate_repeats(self, start_date, end_date):
        if self.year == -1 or self.month == -1 or self.day == -1 or type(self.day) is str:
            start = start_date
            end = end_date
            months = None
            monthdays = None
            weekdays = None
            setpos = None
            freq = DAILY

            if self.start_repeat:
                start = date(self.start_repeat['year'], self.start_repeat['month'], self.start_repeat['day'])
                start += timedelta(self.start_repeat['offset'])
                if start_date > start:
                    start = start_date

            if self.end_repeat:
                end = date(self.end_repeat['year'], self.end_repeat['month'], self.end_repeat['day'])
                end += timedelta(self.end_repeat['offset'])
                if end_date < end:
                    end = end_date

            if self.month == -1:
                months = range(1, 12)
            else:
                months = self.month

            if type(self.day) is int:
                if self.day != -1:
                    monthdays = [self.day]
            else:
                d = self.day
                if d[0] == '<':
                    setpos = 1
                    d = d[1:]
                    freq = MONTHLY
                elif d[-1:] == '>':
                    setpos = -1
                    d = d[:-1]
                    freq = MONTHLY
                for i in range(0, 7):
                    if calendar.day_abbr[i].lower() == d:
                        weekdays = i
                        break

            reps = list(rrule(freq=freq, dtstart=start, until=end, bymonth=months, bymonthday=monthdays, byweekday=weekdays, bysetpos=setpos))
            if self.offset:
                for i in range(len(reps)):
                    reps[i] += timedelta(self.offset)
                    if reps[i].date() < start or reps[i].date() > end:
                        del reps[i]

                return reps
            else:
                return reps
        else:
            d = date(self.year, self.month, self.day)
            d += timedelta(days=self.offset)
            if d >= start_date and d <= end_date:
                return [d]
            return []

    def __repr__(self):
        return "%s" % (self.description)

class Calvin:
    def parse(self, data):
        categories = []
        current_category = Category('All Items')
        categories.append(current_category)

        for line in data.split("\n"):
            if len(line) > 0:
                if line[0] == '#':
                    pass
                elif line[0] == ':':
                    if line[1] == ':':
                        current_category = current_category.add_subcategory(line[2:])
                    else:
                        current_category = Category(line[2:])
                        categories.append(current_category)
                else:
                    current_category.add_item(Event(line))

        return categories

    def usage(self):
        print("""calvin : plain-text calendars""")
        sys.exit(1)

    def main(self, args):
        if len(args) < 1 or (len(args) == 1 and args[0] == '-h'):
            self.usage()

        if not os.path.isfile(args[-1]):
            print('Could not open file %s.' % args[-1], file=sys.stderr)
            sys.exit(1)

        f = open(args[-1])
        cal = self.parse(f.read())

        day1 = date.today()
        day2 = day1
        for i in range(len(args) - 1):
            mod = args[i]
            if mod[-1] == 'd':
                day2 = day2 + timedelta(days=int(mod[:-1]))
            elif mod[-1] == 'D':
                day1 = day1 - timedelta(days=int(mod[:-1]))

        first = True
        for category in cal:
            should_print = False
            if len(category.items) > 0:
                should_print = True
            else:
                for subcategory in category.subcategories:
                    if len(subcategory.items) > 0:
                        should_print = True

            if should_print:
                if not first:
                    print()
                first = False
                print('== %s ==' % category.name)
                for item in category.items:
                    reps = item.generate_repeats(day1, day2)
                    if len(reps) > 0:
                        for d in reps:
                            print('%s %s %s: %s' % (d.year, calendar.month_abbr[d.month], d.day, item))

                for subcategory in category.subcategories:
                    if len(subcategory.items) > 0:
                        print()
                        print('=== %s ===' % subcategory.name)
                        for item in subcategory.items:
                            reps = item.generate_repeats(day1, day2)
                            if len(reps) > 0:
                                for d in reps:
                                    print('%s %s %s: %s' % (d.year, calendar.month_abbr[d.month], d.day, item))

if __name__ == '__main__':
    c = Calvin()
    c.main(sys.argv[1:])
