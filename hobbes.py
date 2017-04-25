#!/usr/bin/env python3

from calvin import Calvin
from datetime import date, timedelta
import calendar
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

class CalendarDay(Gtk.Box):
    def __init__(self, i, off=False, events=[], today=False):
        Gtk.Box.__init__(self)

        day = Gtk.Label('<span size="14000"><b>%s</b></span>' % str(i))
        day.set_xalign(0.95)
        day.set_use_markup(True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        if off:
            day.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#ccc"))
            vbox.add(day)
        else:
            ev = Gtk.VBox(spacing = 5)

            if today:
                day.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#bf2323"))
                vbox.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#ddd'))
            else:
                day.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#888"))

            # self.pop = Gtk.Popover()
            # l = Gtk.Label("popover test")
            # self.pop.add(l)

            for e in events:
                event_box = Gtk.EventBox()

                if e.start_time == '*':
                    label = Gtk.Label('%s' % e.description)
                else:
                    label = Gtk.Label('%s: %s' % (e.start_time, e.description))
                label.set_line_wrap(True)
                label.set_xalign(0.05)
                label.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#555"))
                label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#fff"))

                event_box.add(label)

                # event_box.connect('button-press-event', self.popover)
                ev.pack_end(event_box, True, True, 0)

            vbox.add(day)
            vbox.add(ev)
        self.pack_start(vbox, True, True, 0)

    def popover(self, widget, data=None):
        self.pop.set_relative_to(widget)
        self.pop.show_all()

class CalendarWindow(Gtk.Window):
    def __init__(self, calendar):
        Gtk.Window.__init__(self)
        self.connect('destroy', self.on_destroy)

        self.calendar = calendar

        self.connect('key-press-event', self.on_key_press)

        self.set_size_request(1000, 100)
        self.set_default_size(600, 250)

        self.cal = calendar.Calendar(6)
        self.date = date.today()

        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(False)

        bbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        back = Gtk.Button()
        back.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
        back.connect('clicked', self.prev_month)
        bbox.add(back)

        fbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        forward = Gtk.Button()
        forward.add(Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE))
        forward.connect('clicked', self.next_month)
        fbox.add(forward)

        self.header.pack_start(bbox)
        self.header.pack_end(fbox)

        self.set_titlebar(self.header)

        self.grid = Gtk.Grid()
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_homogeneous(True)
        self.add(self.grid)

        self.refresh()

        self.draw_month()

    def next_month(self, widget, data=None):
        self.month_offset(1)
        self.draw_month()

    def prev_month(self, widget, data=None):
        self.month_offset(-1)
        self.draw_month()

    def month_offset(self, amount):
        month = self.date.month + amount
        year = self.date.year
        if month > 12:
            year += 1
            month = month % 12
        elif month < 1:
            year -= 1
            month = 12
        self.date = date(year, month, 1)

    def normalize_time(self, time):
        if time == '*':
            return 0

        pm = (time[-1] == 'p')
        spl = time.split(':')
        hours = int(spl[0])
        minutes = int(spl[1][:-1])

        if pm:
            hours *= 12

        return hours * 60 + minutes

    def draw_month(self):
        self.grid.foreach(self.grid.remove)
        self.header.props.title = '%s %s' % (calendar.month_name[self.date.month], self.date.year)

        events = {}
        for d in range(1, 32):
            events[d] = []

        next_month = self.date.month + 1
        next_year = self.date.year
        if next_month > 12:
            next_year = self.date.year + 1
            next_month = next_month % 12

        end_date = date(next_year, next_month, 1)
        end_date += timedelta(days=-1)

        for cat in self.calvin:
            for item in cat.items:
                reps = item.generate_repeats(self.date, end_date)
                for r in reps:
                    events[r.day].append(item)
            for scat in cat.subcategories:
                for item in scat.items:
                    reps = item.generate_repeats(self.date, end_date)
                    for r in reps:
                        events[r.day].append(item)

        for e in events:
            events[e] = sorted(events[e], key=lambda ev: self.normalize_time(ev.start_time), reverse=True)

        i = 0
        for day in self.cal.itermonthdates(self.date.year, self.date.month):
            f = Gtk.Frame()
            d = CalendarDay(day.day, day.month != self.date.month, events=events[day.day], today=(day == date.today()))
            d.set_size_request(100, 100)
            f.add(d)
            self.grid.attach(f, i % 7, int(i / 7), 1, 1)
            i += 1

        self.grid.show_all()

    def refresh(self):
        c = Calvin()
        f = open(self.calendar)
        self.calvin = c.parse(f.read())

    def on_key_press(self, widget, data=None):
        if data.keyval == 65361 or data.keyval == 107:
            self.prev_month(None)
        elif data.keyval == 65363 or data.keyval == 106:
            self.next_month(None)
        elif data.keyval == 114:
            self.refresh()
            self.draw_month()
        elif data.keyval == 103:
            self.date = date.today()
            self.draw_month()

    def on_destroy(self, widget, data=None):
        self.destroy()
        Gtk.main_quit()

def main(args):
    if len(args) < 1:
        print('Please specify a calendar file.')
        sys.exit(1)

    window = CalendarWindow(args[1])
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main(argv[1:])
