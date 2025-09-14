"""
Global Market Time Utilities
---------------------------
This module provides utilities for tracking and displaying time-related information
for global financial markets.

Key features:
1. World clock functionality displaying current times in major financial centers
2. Market countdown timer showing time until NYSE market open/close
3. Timezone conversion using pytz for accurate global time representation
4. Streamlit UI components for displaying time information in the dashboard
5. Support for market holidays from both Finnhub API and calculated standard holidays

These utilities help traders and analysts maintain awareness of global market hours
and coordinate activities across different financial centers and trading sessions.
"""


import streamlit as st
import pytz
import requests
import json
import os
from datetime import datetime, timedelta, date
from functools import lru_cache
from config import WORLD_CLOCK_CITIES, MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE, MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE, FINNHUB_API_KEY

def get_world_clock():
    """
    Get current times for major financial centers

    Returns:
        dict: City names and their current times

    Tests:
        >>> wc = get_world_clock()
        >>> set(wc.keys()) == set(WORLD_CLOCK_CITIES.keys())
        True
    """
    world_clock = {}
    for city, timezone_str in WORLD_CLOCK_CITIES.items():
        try:
            tz = pytz.timezone(timezone_str)
            current_time = datetime.now(tz).strftime('%H:%M')
            world_clock[city] = current_time
        except Exception as e:
            # Fallback in case of timezone error
            world_clock[city] = "Error"
            st.error(f"Error getting time for {city}: {str(e)}")
    return world_clock


def display_world_clock():
    """
    Display world clock widget in the Streamlit sidebar

    Tests:
        >>> # Should execute without errors and return None
        >>> display_world_clock() is None
        True
    """
    st.subheader(" World Clock")
    world_clock = get_world_clock()
    for city, time in world_clock.items():
        st.markdown(f"**{city}**: {time}", unsafe_allow_html=True)



def is_weekend(date_obj):
    """
    Check if the given date falls on a weekend (Saturday or Sunday)

    Args:
        date_obj (datetime or date): Date to check

    Returns:
        bool: True if the date is a weekend, False otherwise

    Tests:
        >>> import datetime
        >>> is_weekend(datetime.datetime(2025, 4, 19))  # Saturday
        True
        >>> is_weekend(datetime.date(2025, 4, 21))      # Monday
        False
    """
    if isinstance(date_obj, datetime):
        return date_obj.weekday() >= 5
    else:
        return date_obj.weekday() >= 5



def calculate_easter_sunday(year):
    """
    Calculate Easter Sunday date using Butcher's algorithm

    Args:
        year (int): Year

    Returns:
        date: Date of Easter Sunday

    Tests:
        >>> calculate_easter_sunday(2025)
        datetime.date(2025, 4, 20)
        >>> calculate_easter_sunday(2024)
        datetime.date(2024, 3, 31)
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def calculate_good_friday(year):
    """
    Calculate Good Friday date (2 days before Easter Sunday)

    Args:
        year (int): Year

    Returns:
        date: Date of Good Friday

    Tests:
        >>> calculate_good_friday(2025)
        datetime.date(2025, 4, 18)
        >>> calculate_good_friday(2024)
        datetime.date(2024, 3, 29)
    """
    easter = calculate_easter_sunday(year)
    return easter - timedelta(days=2)


def get_nth_weekday_of_month(year, month, weekday, n):
    """
    Get the nth occurrence of a weekday in a month

    Args:
        year (int): Year
        month (int): Month (1-12)
        weekday (int): Weekday (0=Monday, 6=Sunday)
        n (int): Occurrence (1-5)

    Returns:
        date: Date of the nth weekday

    Tests:
        >>> # 3rd Monday of January 2025 (MLK Day)
        >>> get_nth_weekday_of_month(2025, 1, 0, 3)
        datetime.date(2025, 1, 20)
        >>> # 1st Friday of August 2025
        >>> get_nth_weekday_of_month(2025, 8, 4, 1)
        datetime.date(2025, 8, 1)
    """
    first_day = date(year, month, 1)
    days_until_first = (weekday - first_day.weekday()) % 7
    first_occurrence = first_day + timedelta(days=days_until_first)
    return first_occurrence + timedelta(weeks=n - 1)

def get_last_weekday_of_month(year, month, weekday):
    """
    Get the last occurrence of a weekday in a month

    Args:
        year (int): Year
        month (int): Month (1-12)
        weekday (int): Weekday (0=Monday, 6=Sunday)

    Returns:
        date: Date of the last weekday

    Tests:
        >>> # Last Monday of May 2025 (Memorial Day)
        >>> get_last_weekday_of_month(2025, 5, 0)
        datetime.date(2025, 5, 26)
        >>> # Last Sunday of February 2025
        >>> get_last_weekday_of_month(2025, 2, 6)
        datetime.date(2025, 2, 23)
    """
    if month == 12:
        first_day_next_month = date(year + 1, 1, 1)
    else:
        first_day_next_month = date(year, month + 1, 1)
    last_day = first_day_next_month - timedelta(days=1)
    days_diff = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=days_diff)


def get_standard_market_holidays(year):
    """
    Get standard NYSE market holidays for a given year

    Args:
        year (int): Year to get holidays for

    Returns:
        dict: Dictionary of standard holiday dates and names

    Tests:
        >>> import datetime
        >>> hols = get_standard_market_holidays(2025)
        >>> # New Year's Day on Jan 1, 2025
        >>> hols[datetime.date(2025, 1, 1)]
        "New Year's Day"
        >>> # MLK Day: 3rd Monday in January 2025
        >>> hols[datetime.date(2025, 1, 20)]
        'Martin Luther King Jr. Day'
        >>> # Memorial Day: last Monday in May 2025
        >>> hols[datetime.date(2025, 5, 26)]
        'Memorial Day'
        >>> # Thanksgiving: 4th Thursday in November 2025
        >>> hols[datetime.date(2025, 11, 27)]
        'Thanksgiving Day'
    """
    holidays = {}

    # New Year's Day
    new_years = date(year, 1, 1)
    if new_years.weekday() == 5:
        holidays[date(year - 1, 12, 31)] = "New Year's Day (Observed)"
    elif new_years.weekday() == 6:
        holidays[date(year, 1, 2)] = "New Year's Day (Observed)"
    else:
        holidays[new_years] = "New Year's Day"

    # MLK Day (3rd Monday in January)
    holidays[get_nth_weekday_of_month(year, 1, 0, 3)] = "Martin Luther King Jr. Day"

    # Presidents' Day (3rd Monday in February)
    holidays[get_nth_weekday_of_month(year, 2, 0, 3)] = "Presidents' Day"

    # Good Friday
    holidays[calculate_good_friday(year)] = "Good Friday"

    # Memorial Day (Last Monday in May)
    holidays[get_last_weekday_of_month(year, 5, 0)] = "Memorial Day"

    # Juneteenth
    juneteenth = date(year, 6, 19)
    if juneteenth.weekday() == 5:
        holidays[date(year, 6, 18)] = "Juneteenth (Observed)"
    elif juneteenth.weekday() == 6:
        holidays[date(year, 6, 20)] = "Juneteenth (Observed)"
    else:
        holidays[juneteenth] = "Juneteenth"

    # Independence Day
    independence_day = date(year, 7, 4)
    if independence_day.weekday() == 5:
        holidays[date(year, 7, 3)] = "Independence Day (Observed)"
    elif independence_day.weekday() == 6:
        holidays[date(year, 7, 5)] = "Independence Day (Observed)"
    else:
        holidays[independence_day] = "Independence Day"

    # Labor Day (1st Monday in September)
    holidays[get_nth_weekday_of_month(year, 9, 0, 1)] = "Labor Day"

    # Thanksgiving (4th Thursday in November)
    holidays[get_nth_weekday_of_month(year, 11, 3, 4)] = "Thanksgiving Day"

    # Christmas
    christmas = date(year, 12, 25)
    if christmas.weekday() == 5:
        holidays[date(year, 12, 24)] = "Christmas Day (Observed)"
    elif christmas.weekday() == 6:
        holidays[date(year, 12, 26)] = "Christmas Day (Observed)"
    else:
        holidays[christmas] = "Christmas Day"

    return holidays


def get_cache_file_path(year):
    """
    Get the path to the cache file for market holidays

    Args:
        year (int): Year for the cache file

    Returns:
        str: Path to the cache file

    Tests:
        >>> p = get_cache_file_path(2025)
        >>> isinstance(p, str)
        True
        >>> p.endswith('market_holidays_2025.json')
        True
    """
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"market_holidays_{year}.json")


def fetch_market_holidays_from_finnhub(year):
    """
    Fetch market holidays from Finnhub API with explicit date range

    Args:
        year (int): Year to fetch holidays for

    Returns:
        dict: Dictionary of holiday dates and names

    Tests:
        >>> h = fetch_market_holidays_from_finnhub(1900)
        >>> isinstance(h, dict)
        True
    """
    try:
        # Finnhub API endpoint for market holidays
        url = "https://finnhub.io/api/v1/calendar/holiday"

        # Set up the parameters with explicit date range
        params = {
            "exchange": "US",  # US exchange
            "from": f"{year}-01-01",
            "to": f"{year}-12-31",
            "token": FINNHUB_API_KEY
        }

        # Make the API request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Debug the API response (uncomment to see the raw response)
        # st.write("Finnhub API Response:", data)

        api_holidays = {}

        # Process the response based on the documented structure
        if "data" in data and data["data"]:
            for holiday in data["data"]:
                # Get the holiday date
                holiday_date = datetime.strptime(holiday["atDate"], "%Y-%m-%d").date()

                # Only include holidays for the requested year
                if holiday_date.year == year:
                    # Check if it's a full day closure or early close
                    trading_hour = holiday.get("tradingHour", "")
                    if not trading_hour:  # Empty string means full day closure
                        api_holidays[holiday_date] = holiday["eventName"]
                    else:
                        # Early close
                        api_holidays[holiday_date] = f"{holiday['eventName']} (Early Close: {trading_hour})"

            # Just return what we got from Finnhub
            return api_holidays

        # If we couldn't get holiday data or none were found for this year
        return {}

    except Exception as e:
        # Log the error but don't stop execution
        st.warning(f"Error fetching holiday data from Finnhub API: {str(e)}")
        return {}


@lru_cache(maxsize=10)
@lru_cache(maxsize=10)
def get_market_holidays(year=None):
    """
    Get a dictionary of all US stock market holidays for a specific year
    Combines data from Finnhub API and calculated standard holidays

    Args:
        year (int, optional): Year to get holidays for. Defaults to current year.

    Returns:
        dict: Dictionary of holiday dates and names

    Tests:
        >>> # Requesting a specific past year should include known holidays
        >>> hols_2025 = get_market_holidays(2025)
        >>> import datetime
        >>> # Good Friday 2025
        >>> datetime.date(2025, 4, 18) in hols_2025
        True
        >>> # Christmas Day 2025
        >>> datetime.date(2025, 12, 25) in hols_2025
        True
        >>> # Cache behavior: repeated call returns same dict object (due to lru_cache)
        >>> hols_again = get_market_holidays(2025)
        >>> hols_again is hols_2025
        True
    """
    if year is None:
        year = datetime.now().year

    cache_file = get_cache_file_path(year)
    today = datetime.now().date()

    # Use the cache if it exists and was updated today
    if os.path.exists(cache_file):
        try:
            cache_stat = os.stat(cache_file)
            cache_date = datetime.fromtimestamp(cache_stat.st_mtime).date()
            if cache_date == today:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                holidays = {}
                for date_str, name in cached_data.items():
                    holiday_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    holidays[holiday_date] = name
                return holidays
        except (json.JSONDecodeError, ValueError, KeyError):
            pass

    standard_holidays = get_standard_market_holidays(year)
    finnhub_holidays = fetch_market_holidays_from_finnhub(year)
    combined_holidays = {**standard_holidays, **finnhub_holidays}

    try:
        with open(cache_file, 'w') as f:
            serializable = {d.strftime("%Y-%m-%d"): n for d, n in combined_holidays.items()}
            json.dump(serializable, f)
    except (IOError, PermissionError) as e:
        st.warning(f"Error writing to holiday cache: {str(e)}")

    return combined_holidays


def is_market_holiday(date_obj):
    """
    Check if the given date is a US market holiday

    Args:
        date_obj (datetime or date): Date to check

    Returns:
        bool: True if the date is a market holiday, False otherwise

    Tests:
        >>> import datetime
        >>> is_market_holiday(datetime.date(2025, 4, 18))  # Good Friday 2025
        True
        >>> is_market_holiday(datetime.date(2025, 4, 21))  # Regular Monday
        False
    """
    check_date = date_obj.date() if isinstance(date_obj, datetime) else date_obj
    year_holidays = get_market_holidays(check_date.year)
    return check_date in year_holidays


def get_holiday_name(date_obj):
    """
    Get the name of the holiday for a given date

    Args:
        date_obj (datetime or date): Date to check

    Returns:
        str: Name of the holiday, or None if it's not a holiday

    Tests:
        >>> import datetime
        >>> get_holiday_name(datetime.date(2025, 4, 18))  # Good Friday 2025
        'Good Friday'
        >>> get_holiday_name(datetime.date(2025, 4, 21)) is None
        True
    """
    check_date = date_obj.date() if isinstance(date_obj, datetime) else date_obj
    year_holidays = get_market_holidays(check_date.year)
    return year_holidays.get(check_date)


def get_next_business_day(date_obj):
    """
    Get the next business day (excluding weekends and holidays)

    Args:
        date_obj (datetime or date): Starting date

    Returns:
        date: Next business day

    Tests:
        >>> import datetime
        >>> # Feb 1, 2025 is a Saturday → next business day is Monday Feb 3, 2025
        >>> get_next_business_day(datetime.date(2025, 2, 1))
        datetime.date(2025, 2, 3)
        >>> # If the next day is a holiday (Good Friday 2025 on Apr 18), skip to Apr 21
        >>> get_next_business_day(datetime.date(2025, 4, 17))
        datetime.date(2025, 4, 21)
    """
    if isinstance(date_obj, datetime):
        check_date = date_obj.date() + timedelta(days=1)
    else:
        check_date = date_obj + timedelta(days=1)

    max_iterations = 30
    iterations = 0

    while (is_weekend(check_date) or is_market_holiday(check_date)) and iterations < max_iterations:
        check_date += timedelta(days=1)
        iterations += 1

    return check_date


def get_market_status():
    """
    Determine current market status: open, closed for the day, weekend, or holiday

    Returns:
        str: Market status message

    Tests:
        >>> # Should always return one of the expected status formats
        >>> res = get_market_status()
        >>> isinstance(res, str)
        True
        >>> res in ("OPEN", "CLOSED (Weekend)", "CLOSED (After Hours)") or res.startswith("CLOSED (")
        True
    """
    ny_tz = pytz.timezone("America/New_York")
    now = datetime.now(ny_tz)
    today = now.date()

    if is_weekend(now):
        return "CLOSED (Weekend)"
    if is_market_holiday(now):
        holiday_name = get_holiday_name(now)
        return f"CLOSED ({holiday_name})"

    market_open = now.replace(
        hour=MARKET_OPEN_HOUR,
        minute=MARKET_OPEN_MINUTE,
        second=0,
        microsecond=0
    )
    market_close = now.replace(
        hour=MARKET_CLOSE_HOUR,
        minute=MARKET_CLOSE_MINUTE,
        second=0,
        microsecond=0
    )

    if market_open <= now < market_close:
        return "OPEN"
    else:
        return "CLOSED (After Hours)"


def get_market_countdown():
    """
    Calculate time until market opens/closes (based on NY time)
    Accounts for weekends and holidays

    Returns:
        tuple: (countdown_string, status_message)

    Tests:
        >>> # Should return a tuple of two strings
        >>> cd, st_msg = get_market_countdown()
        >>> isinstance(cd, str) and isinstance(st_msg, str)
        True
        >>> # Status should start with expected prefixes
        >>> any(st_msg.startswith(prefix) for prefix in ("Market opens in:", "Market closes in:"))
        True
    """
    ny_tz = pytz.timezone("America/New_York")
    now = datetime.now(ny_tz)
    today = now.date()

    market_open = now.replace(
        hour=MARKET_OPEN_HOUR,
        minute=MARKET_OPEN_MINUTE,
        second=0,
        microsecond=0
    )
    market_close = now.replace(
        hour=MARKET_CLOSE_HOUR,
        minute=MARKET_CLOSE_MINUTE,
        second=0,
        microsecond=0
    )

    # Weekend or holiday
    if is_weekend(today) or is_market_holiday(today):
        next_bd = get_next_business_day(today)
        next_open = datetime.combine(next_bd, datetime.min.time(), tzinfo=ny_tz).replace(
            hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE)
        status_extra = ""
        if is_market_holiday(today):
            status_extra = f" (After {get_holiday_name(today)})"
        else:
            status_extra = " (After Weekend)"
        delta = next_open - now
        days, rem = delta.days, delta.seconds
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        return f"{days}d {h}h {m}m {s}s", f"Market opens in{status_extra}:"

    # Normal weekday logic
    if now < market_open:
        delta = market_open - now
        status = "Market opens in:"
    elif now < market_close:
        delta = market_close - now
        status = "Market closes in:"
    else:
        tomorrow = today + timedelta(days=1)
        if is_weekend(tomorrow) or is_market_holiday(tomorrow):
            next_bd = get_next_business_day(today)
        else:
            next_bd = tomorrow
        next_open = datetime.combine(next_bd, datetime.min.time(), tzinfo=ny_tz).replace(
            hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE)
        delta = next_open - now
        status = "Market opens in:"
        days, rem = delta.days, delta.seconds
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        return f"{days}d {h}h {m}m {s}s", status

    h, rem = divmod(delta.seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s", status


def display_next_holiday():
    """
    Display the next upcoming market holiday

    Tests:
        >>> # Should execute without errors and return None
        >>> display_next_holiday() is None
        True
    """
    ny_tz = pytz.timezone("America/New_York")
    today = datetime.now(ny_tz).date()

    # Get holidays for current and next year
    current_year_holidays = get_market_holidays(today.year)
    next_year_holidays = get_market_holidays(today.year + 1)

    # Combine both dictionaries
    all_holidays = {**current_year_holidays, **next_year_holidays}

    # Sort by date
    holidays_list = sorted(all_holidays.items(), key=lambda x: x[0])

    # Filter for upcoming
    upcoming_holidays = [(d, n) for d, n in holidays_list if d >= today]

    if upcoming_holidays:
        next_date, next_name = upcoming_holidays[0]
        days_until = (next_date - today).days

        st.markdown(f"**Next Market Holiday:** {next_name} ({next_date.strftime('%a, %b %d, %Y')})", unsafe_allow_html=True)
        st.markdown(f"**Days Until:** {days_until}", unsafe_allow_html=True)

        if len(upcoming_holidays) > 1:
            following_date, following_name = upcoming_holidays[1]
            following_days = (following_date - today).days
            st.markdown(f"**Following Holiday:** {following_name} ({following_date.strftime('%a, %b %d, %Y')})", unsafe_allow_html=True)
            st.markdown(f"**Days Until:** {following_days}", unsafe_allow_html=True)
    else:
        st.markdown("**No upcoming market holidays found**", unsafe_allow_html=True)


def display_holiday_source():
    """
    Display information about the source of market holiday data

    Tests:
        >>> # Should execute without errors and return None
        >>> display_holiday_source() is None
        True
    """
    cache_file = get_cache_file_path(datetime.now().year)
    if os.path.exists(cache_file):
        cache_stat = os.stat(cache_file)
        cache_date = datetime.fromtimestamp(cache_stat.st_mtime).date()
        cache_time = datetime.fromtimestamp(cache_stat.st_mtime).strftime("%H:%M:%S")
        st.markdown(f"*Holiday data last updated: {cache_date.strftime('%b %d, %Y')} at {cache_time}*")
    else:
        st.markdown("*Using calculated holiday data*")


def display_countdown_timer():
    """
    Display market countdown timer in the Streamlit sidebar

    Tests:
        >>> # Should execute without errors and return None
        >>> display_countdown_timer() is None
        True
    """
    countdown, status = get_market_countdown()
    market_status = get_market_status()

    st.subheader(" Market Countdown")
    st.markdown(f"**Status:** {market_status}", unsafe_allow_html=True)
    st.markdown(f"**{status}** {countdown}", unsafe_allow_html=True)

    st.subheader(" Upcoming Market Holidays")
    display_next_holiday()
    display_holiday_source()

    if st.button("Refresh Holiday Data"):
        get_market_holidays.cache_clear()
        cache_file = get_cache_file_path(datetime.now().year)
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except (OSError, PermissionError):
                pass
        current_year = datetime.now().year
        get_market_holidays(current_year)
        get_market_holidays(current_year + 1)
        st.success("Holiday data refreshed!")
        st.rerun()

