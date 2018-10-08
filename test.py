import matplotlib.pyplot as plt
import numpy as np
from math import floor, ceil

# Moon Table
MOON_TAB = (0, 5, 10, 15, 19, 22, 24, 25)
SUN_TAB	 = (0, 6, 10, 11)

# moon_tab_int($i): moon_tab for integer values.
def _moon_tab_int(i):
  i = i % 28
  if i <= 7:
  	return MOON_TAB[i]
  if i <= 14:
  	return MOON_TAB[14 - i]
  if i <= 21:
  	return - MOON_TAB[i - 14]
  return - MOON_TAB[28 - i];

def _moon_tab(i):
	u = _moon_tab_int(int(ceil(i)))
	d = _moon_tab_int(int(floor(i)))
	return d + (i - floor(i)) * (u - d)

A1 = 253.0  / 3528;
A2 = 1.0 / 28;
# use constant A2	=> 1/28 + 1/105840; # not used; see Janson, p. 17, bottom.
A0 = 475.0 / 3528;

# moon_anomaly($day, $month_count)
def _moon_anomaly(day, month_count):
	return month_count * A1 + day * A2 + A0

# # moon_equ($day, $month_count): Equation of the moon.
def _moon_equ(day, month_count):
	return _moon_tab(28 * _moon_anomaly(day, month_count))


# sun_tab_int($i): Sun tab for integer values
def _sun_tab_int(i):
	i = i % 12
	if i <= 3:
		return SUN_TAB[i]
	if i <= 6:
		return SUN_TAB[6 - i]
	if i <= 9:
		return -SUN_TAB[i - 6]
	return -SUN_TAB[12 - i]

def _sun_tab(i): # sun tab, with linear interpolation.
	u = _sun_tab_int(int(ceil(i)))
	d = _sun_tab_int(int(floor(i)))
	return d + (i - floor(i)) * (u - d)

S1 = 65.0/804;
S0 = 743.0/804;
S2 = S1 / 30;
# mean_sun($day, $month_count)
def _mean_sun(day, month_count):
	return month_count * S1 + day * S2 + S0;

# # sun_equ($day, $month_count): Equation of the sun.
def _sun_equ(day, month_count):
	return _sun_tab(12.0 * (mean_sun(day, month_count) - 1.0/4));

M1 = 167025.0 / 5656; # the period of moon, 29.53
M2 = M1 / 30;
M0 = 2015501.0 + 4783.0 / 5656;

# mean_date($day, $month_count)
def _mean_date(d, n):
	return n * M1 + d * M2 + M0;

# true_date($day, $month_count)
def _true_date(d, n):
	return _mean_date(d, n) + _moon_equ(d, n) / 60 - _sun_equ(d, n) / 60;

# day_before($day, $month_count): substract 1 day from a date
def _day_before(d, n):
	if d == 1:
		return (30, n - 1)
	else:
		return (d - 1, n)


WEEKDAYS = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')
# year elements & animals
YEAR_ELEMENTS = ('Wood', 'Fire', 'Earth', 'Iron', 'Water')
YEAR_ANIMALS = ('Mouse', 'Ox', 'Tiger', 'Rabbit', 'Dragon',
	'Snake', 'Horse', 'Sheep', 'Monkey', 'Bird', 'Dog', 'Pig')
YEAR_GENDER = ('Male', 'Female')

# print(type(SUN_TAB))
# week day from julian day
def weekday(jd):
	return WEEKDAYS[(jd + 1) % 7]

# figure out the animal and element for a tibetan year
def year_attributes(year):
	Y = int(year['tib_year'])
	year['animal'] = YEAR_ANIMALS[(Y + 1) % 12];
 	year['element'] = YEAR_ELEMENTS[((Y - 1) / 2) % 5];
 	year['gender'] = YEAR_GENDER[(Y + 1) % 2];
 	return year


#  Figures out a year's info based on the Tibetan calendar, ex. the 3rd year of
# the 15th Rabjung calendrical cycle.  
# Inputs:
#   $cycle_no : number of the cycle
#   $year_no  : number of the year within the cycle, from 1 to 60.
# Returns: a hashref with the following elements:
#   cycle_no  : number of the cycle
#   year_no   : number of the year within the cycle, from 1 to 60.
#   western_year : western year during which most of the given tibetan year falls
#   tib_year  : tibetan year number (i.e western year + 127)
def rabjung_year(cycle_no, year_no):
	if year_no < 1 or year_no > 60:
		raise
	year = {'cycle_no': cycle_no,
		    'year_no': year_no,
		    'western_year': (966 + year_no + 60 * cycle_no)}
	year['tib_year'] = year['western_year'] + 127
	return year_attributes(year)

# Figures out a year's info from a Western calendar year number, ex. 2008.
# Returns: same as rabjung_year().
def mod(x, n):
	return x % n
def amod(x, n):
	if mod(x, n) == 0:
		return n
	return mod(x, n)

def western_year(w_year):
	year = {
	    'cycle_no': ceil((w_year - 1026) / 60),
	    'year_no': amod(w_year - 6, 60),
	    'tib_year': w_year + 127,
	    'western_year': w_year}
    return year_attributes(year)

# Figures out a year's info from a Tibetan calendar year number, ex. 2135.
# Returns: same as rabjung_year().
def tibetan_year(y):
  return western_year(y - 127)


ALPHA = 1 + 827/1005
BETA = 123
# from_month_count($n)
#
# Figures out the Tibetan year number, month number within the year, and whether
# this is a leap month, from a "month count" number.  See Svante Janson, 
# "Tibetan Calendar Mathematics", p.8 ff.
# 
# Returns: ($year, $month, $is_leap_month)
def from_month_count(n):
	x = ceil(12 * S1 * n + ALPHA);
	M = amod(x, 12);
	Y = (x - M) / 12 + Y0 + 127;
	l = (ceil(12 * S1 * (n + 1) + ALPHA) == x)
	return (Y, M, l)

# to_month_count($year, $month, $is_leap_month)
#
# This is the reverse of from_month_count(): from a Tibetan year, month number
# and leap month indicator, calculates the "month count" based on the epoch.
def to_month_count(Y, M, l):
	Y-=127		# the formulas on Svante's paper use western year numbers
	l = int(l)
	return floor((12 * (Y - Y0) + M - ALPHA - (1 - 12 * S1) * l) / (12 * S1))

# =head2 has_leap_month($year, $month)
# Calculates whether a given Tibetan year and month number is duplicated, i.e
# is preceded by a leap month.
# =cut
def has_leap_month(Y, M):
	Mp = 12 * (Y - 127 - Y0) + M
	return ((2 * Mp) % 65 == BETA % 65) || ((2 * Mp) % 65 == (BETA + 1) % 65)

