import argparse
import datetime

import togglore
from togglore import utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool for toggle to calculate over/undertime.')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    parser_range = subparsers.add_parser('range', help='range help')
    parser_range.add_argument('from_date', help='startdate, e.g. 30.08.2016')
    parser_range.add_argument('to_date', help='enddate, e.g. 12.10.2016')

    parser_year = subparsers.add_parser('thisyear', help='today help')
    parser_month = subparsers.add_parser('thismonth', help='month help')
    parser_week = subparsers.add_parser('thisweek', help='week help')
    parser_today = subparsers.add_parser('today', help='day help')

    args = parser.parse_args()

    client = togglore.Togglore()

    expected = 0
    actual = 0

    if args.command == 'range':
        actual, expected = client.diff(utils.DateRange.parse_from_iso_strings(args.from_date, args.to_date))
    elif args.command == 'thisyear':
        actual, expected = client.diff(utils.DateRange.this_year())
    elif args.command == 'thismonth':
        actual, expected = client.diff(utils.DateRange.this_month())
    elif args.command == 'thisweek':
        actual, expected = client.diff(utils.DateRange.this_week())
    elif args.command == 'today':
        actual, expected = client.diff(utils.DateRange.today())

    print("Hours to do: {}".format(expected))
    print("Hours worked: {}".format(actual))

    print("Difference: {}".format(actual-expected))