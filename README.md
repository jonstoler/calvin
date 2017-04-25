# calvin

**Current version:** 0.1

Calvin is a command-line, plaintext calendar program. It is designed to be easy to learn but flexible. You can think of it as a simpler version of [remind](https://roaringpenguin.com/products/remind).

Calvin also ships with an experimental GUI calendar, Hobbes.

Calvin can also be used as a Python library.

## `calvin` CLI Usage

	calvin (time period) [CALENDAR FILE]

Where time period is in the form `Xd` to show `X` days ahead and `YD` to show `Y` days behind. These can be chained; `Xd YD` will show events that fall within the past `Y` days and up to the next `X` days.

If time period is left out, calvin will only show events for the current day.

## Software Status

### Calvin

Calvin is usable but not finished. Planned features:
* Cleaner, better source code
* Colored terminal output
* More options and time period options
* Daemon mode (for event alerts)
* Android Calendar Provider

### Hobbes

Hobbes is usable but lacks many important calendar features. Planned features:
* Cleaner, better source code
* Quick navigation
* Colored events (based on category and subcategory)
* Show/hide categories and subcategories
* Built-in calendar editor

## Calvin File Format

A calvin file (extension `.calvin`) is made up of comments, categories, and events. Each line is either a comment, category, event, or blank.

### Comments

Lines that begin with a hash (`#`) are comments. Comments go until the end of their lines, and must take up their entire line.

	# This line is a comment.

### Categories

Lines that begin with a colon are categories. Optionally, these lines can also end with a colon.

	: Category Name :
	: Another Category :

#### Subcategories

Lines that begin with two colons are subcategories. Optionally, these lines can also end with two colons

	:: Subcategory
	:: Another Subcategory ::

### Events

Lines that are not comments, categories, subcategories, or whitespace must be events.

Events are required to have the following properties: date, time, and description.

Events may additionally have the following properties: start date, stop date, duration, and location.

#### Dates

Dates must contain a year, month, and day. Dates may optionally contain an offset.

To write a date, start with a four-digit year, followed by a space, then the short name of a month (Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sept, Oct, Nov, Dec), followed by a space, then a day (optionally zero-padded). Month names are not case-sensitive.

	# Groundhog Day!
	2017 Feb 02

Dates can also contain an offset. After the day, write a space, then a plus or minus and an offset. Offsets are measured in days.

	# Still Groundhog Day!
	2017 Feb 03 -1
	2017 Feb 01 +1

To have a date repeat every year, replace the year with a glob (`*`).

	# Every Groundhog Day
	* Feb 02

To have a date repeat every month, replace the month with a glob (`*`).

	# Every first of the month
	* * 01

To have a date repeat every week, replace the day with a weekday abbreviation (Sun, Mon, Tues, Wed, Thurs, Fri, Sat). Weekday names are not case-sensitive.

	# Party every Friday!
	* * Fri

To use the first occurrence of a given weekday in a month, place an open brace (`<`) before the weekday abbreviation.

	# The first Monday of June
	* Jun <Mon
	
	# Thanksgiving
	* Nov <Thurs +21

To use the last occurrence of a given weekday in a month, place a closed brace (`>`) after the weekday abbreviation.

	# The last Friday of June
	* Jun Fri>

#### Start Date (Optional)

To specify a start date for repeat events, add a space, tilde (`~`), and another space, then write the start date. Start dates are inclusive. Start dates cannot contain globs.

	# Every Monday starting in 2017
	2017 * Mon ~ 2017 Jan 01

#### Stop Date (Optional)

To specify a stop date for repeat events, add a space, arrow (`->`), and another space, then write the stop date. Stop dates are exclusive. Stop dates cannot contain globs.

	# Every Monday until the second-to-last Monday in June in 2017
	2017 * Mon -> 2017 Jun Mon> -7

	# Every Monday between February and April
	2017 * Mon ~ 2017 Feb 01 -> 2017 Apr 01

#### Time

To specify a time, write the hour (with optional padded zero), a colon, then the minutes, then `a` for AM or `p` for PM.

	# Lunch time!
	* * * 11:00a

	# Sleep time!
	* * * 10:30p

To create an all-day event, use a glob (`*`) for the time.

	# Busy day!
	2017 Dec 25 *

#### Duration (Optional)

To specify a duration, write a dash (`-`) after the time, then an end time.

	# Lunch break
	* * * 11:00a-12:00p

	# Sleeping
	* * * 10:30p-08:00a

#### Description

To add a description, write a space, then a colon, then a space, followed by a description of what the event is. Event descriptions go until the end of their lines, or until a location.

	# Favorite holiday
	* Feb 02 * : Groundhog Day

#### Location (Optional)

To add a location, write a space, then an ampersat (`@`), then a space, followed by the location of an event. Locations go until the end of their line.

	# Favorite holiday at my favorite place
	* Feb 02 * : Groundhog Day @ Punxsutawney, PA

#### Putting It All Together

Overall, an event looks like the following (optional components are surrounded by parentheses):

	YEAR MONTH DAY (+/-OFFSET) TIME(-END TIME) (~START DATE) (-> END DATE) : DESCRIPTION (@ LOCATION)
