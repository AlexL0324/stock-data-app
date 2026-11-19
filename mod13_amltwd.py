
import re
import unittest
from datetime import date, datetime


# ---------------------------------------------------------------- validators
def is_valid_symbol(value):
    """Capitalized, 1-7 alphabetic characters (A-Z only)."""
    return isinstance(value, str) and re.fullmatch(r"[A-Z]{1,7}", value) is not None


def is_valid_chart_type(value):
    """Exactly one numeric character, '1' or '2'."""
    return isinstance(value, str) and re.fullmatch(r"[1-2]", value) is not None


def is_valid_time_series(value):
    """Exactly one numeric character, '1' through '4'."""
    return isinstance(value, str) and re.fullmatch(r"[1-4]", value) is not None


def is_valid_date(value):
    """A real calendar date written strictly as YYYY-MM-DD."""
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def is_valid_date_range(start, end):
    """Both dates valid and the end date is not before the begin date."""
    if not (is_valid_date(start) and is_valid_date(end)):
        return False
    return datetime.strptime(end, "%Y-%m-%d").date() >= datetime.strptime(start, "%Y-%m-%d").date()


# --------------------------------------------------------------------- tests
class TestSymbol(unittest.TestCase):
    def test_valid_symbols(self):
        for s in ["A", "IBM", "AAPL", "GOOGL", "ABCDEFG"]:
            with self.subTest(symbol=s):
                self.assertTrue(is_valid_symbol(s))

    def test_empty_symbol(self):
        self.assertFalse(is_valid_symbol(""))

    def test_too_long(self):
        self.assertFalse(is_valid_symbol("ABCDEFGH"))  # 8 characters

    def test_lowercase_rejected(self):
        for s in ["ibm", "Ibm", "aAPL"]:
            with self.subTest(symbol=s):
                self.assertFalse(is_valid_symbol(s))

    def test_non_alpha_rejected(self):
        for s in ["IB1", "123", "IB M", "IBM!", "BRK.B", "IBM\n", " IBM"]:
            with self.subTest(symbol=s):
                self.assertFalse(is_valid_symbol(s))

    def test_non_string_rejected(self):
        for s in [None, 123, 1.5, ["IBM"]]:
            with self.subTest(symbol=s):
                self.assertFalse(is_valid_symbol(s))


class TestChartType(unittest.TestCase):
    def test_valid_choices(self):
        for c in ["1", "2"]:
            with self.subTest(choice=c):
                self.assertTrue(is_valid_chart_type(c))

    def test_out_of_range_numbers(self):
        for c in ["0", "3", "9"]:
            with self.subTest(choice=c):
                self.assertFalse(is_valid_chart_type(c))

    def test_multiple_characters(self):
        for c in ["11", "12", "10", "1 ", " 1"]:
            with self.subTest(choice=c):
                self.assertFalse(is_valid_chart_type(c))

    def test_non_numeric(self):
        for c in ["a", "A", "!", "", "one"]:
            with self.subTest(choice=c):
                self.assertFalse(is_valid_chart_type(c))

    def test_non_string_rejected(self):
        for c in [None, 1, 2, 1.0]:
            with self.subTest(choice=c):
                self.assertFalse(is_valid_chart_type(c))


class TestTimeSeries(unittest.TestCase):
    def test_valid_choices(self):
        for c in ["1", "2", "3", "4"]:
            with self.subTest(choice=c):
                self.assertTrue(is_valid_time_series(c))

    def test_out_of_range_numbers(self):
        for c in ["0", "5", "9"]:
            with self.subTest(choice=c):
                self.assertFalse(is_valid_time_series(c))

    def test_multiple_characters(self):
        for c in ["12", "14", "10", "44", "1 "]:
            with self.subTest(choice=c):
                self.assertFalse(is_valid_time_series(c))

    def test_non_numeric(self):
        for c in ["a", "x", "#", "", "two"]:
            with self.subTest(choice=c):
                self.assertFalse(is_valid_time_series(c))

    def test_non_string_rejected(self):
        for c in [None, 3, 4.0]:
            with self.subTest(choice=c):
                self.assertFalse(is_valid_time_series(c))


class DateTestsMixin:
    """Shared checks for the begin date and end date inputs."""

    def check(self, value):
        raise NotImplementedError

    def test_valid_dates(self):
        for d in ["2024-01-01", "2023-12-31", "2000-02-29", "1999-06-15"]:
            with self.subTest(date=d):
                self.assertTrue(self.check(d))

    def test_leap_day_rules(self):
        self.assertTrue(self.check("2024-02-29"))   # leap year
        self.assertFalse(self.check("2023-02-29"))  # not a leap year
        self.assertFalse(self.check("1900-02-29"))  # century, not leap

    def test_impossible_dates(self):
        for d in ["2024-13-01", "2024-00-10", "2024-04-31", "2024-01-32", "2024-01-00"]:
            with self.subTest(date=d):
                self.assertFalse(self.check(d))

    def test_wrong_format(self):
        for d in ["01-01-2024", "2024/01/01", "20240101", "2024-1-1",
                  "2024-01-1", "24-01-01", "Jan 1 2024", "2024.01.01"]:
            with self.subTest(date=d):
                self.assertFalse(self.check(d))

    def test_empty_and_whitespace(self):
        for d in ["", " ", " 2024-01-01", "2024-01-01 ", "2024-01-01\n"]:
            with self.subTest(date=repr(d)):
                self.assertFalse(self.check(d))

    def test_non_date_text(self):
        for d in ["abcd-ef-gh", "yyyy-mm-dd", "tomorrow", "2024-AB-01"]:
            with self.subTest(date=d):
                self.assertFalse(self.check(d))

    def test_non_string_rejected(self):
        for d in [None, 20240101, date(2024, 1, 1)]:
            with self.subTest(date=d):
                self.assertFalse(self.check(d))


class TestStartDate(DateTestsMixin, unittest.TestCase):
    def check(self, value):
        return is_valid_date(value)


class TestEndDate(DateTestsMixin, unittest.TestCase):
    def check(self, value):
        return is_valid_date(value)


class TestDateRange(unittest.TestCase):
    def test_end_after_start(self):
        self.assertTrue(is_valid_date_range("2024-01-01", "2024-06-30"))

    def test_same_day_allowed(self):
        self.assertTrue(is_valid_date_range("2024-03-15", "2024-03-15"))

    def test_end_before_start_rejected(self):
        self.assertFalse(is_valid_date_range("2024-06-30", "2024-01-01"))
        self.assertFalse(is_valid_date_range("2024-01-02", "2024-01-01"))

    def test_range_across_year_boundary(self):
        self.assertTrue(is_valid_date_range("2023-12-31", "2024-01-01"))

    def test_invalid_date_in_range_rejected(self):
        self.assertFalse(is_valid_date_range("2024-13-01", "2024-12-31"))
        self.assertFalse(is_valid_date_range("2024-01-01", "not-a-date"))


if __name__ == "__main__":
    unittest.main(verbosity=2)