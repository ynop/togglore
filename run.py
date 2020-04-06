import argparse

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
    parser_thismonth = subparsers.add_parser('thismonth', help='month help')
    parser_lastmonth = subparsers.add_parser('lastmonth', help='last month help')
    parser_week = subparsers.add_parser('thisweek', help='week help')
    parser_lastweek = subparsers.add_parser('lastweek', help='this week help')
    parser_today = subparsers.add_parser('today', help='day help')
    parser_month = subparsers.add_parser('month', help='month help')
    parser_month.add_argument('month', help='month e.g. 08')
    parser_since = subparsers.add_parser('since', help='since help')
    parser_since.add_argument('since', help='since e.g. 2016.08.01')

    parser.add_argument(
        '--untiltoday',
        action="store_true",
    )

    parser.add_argument(
        '--notify',
        action="store_true",
    )

    parser.add_argument(
        '--uses_notify_send',
        action="store_true",
    )

    args = parser.parse_args()

    client = togglore.Togglore()

    expected = 0
    actual = 0
    running = 0

    if args.command == 'range':
        actual, expected, running = client.diff(utils.DateRange.parse_from_iso_strings(args.from_date, args.to_date))
    elif args.command == 'thisyear':
        if args.untiltoday:
            actual, expected, running = client.diff(utils.DateRange.this_year_until_today(), include_running=True)
        else:
            actual, expected, running = client.diff(utils.DateRange.this_year(), include_running=True)
    elif args.command == 'thismonth':
        if args.untiltoday:
            actual, expected, running = client.diff(utils.DateRange.this_month_until_today(), include_running=True)
        else:
            actual, expected, running = client.diff(utils.DateRange.this_month(), include_running=True)
    elif args.command == 'lastmonth':
            actual, expected, running = client.diff(utils.DateRange.last_month())
    elif args.command == 'thisweek':
        if args.untiltoday:
            actual, expected, running = client.diff(utils.DateRange.this_week_until_today(), include_running=True)
        else:
            actual, expected, running = client.diff(utils.DateRange.this_week(), include_running=True)
    elif args.command == 'lastweek':
        actual, expected, running = client.diff(utils.DateRange.last_week())
    elif args.command == 'today':
        actual, expected, running = client.diff(utils.DateRange.today(), include_running=True)
    elif args.command == 'month':
        actual, expected, running = client.diff(utils.DateRange.month(int(args.month)))
    elif args.command == 'since':
        actual, expected, running = client.diff(utils.DateRange.since(args.since))


    difference = actual-expected

    brl = float(client.cfg.eur_to_brl['value'])
    brl_update_date = client.cfg.eur_to_brl['date']
    actual_eur = actual * client.cfg.hourly_wage
    actual_brl = actual_eur * brl
    expected_eur = expected * client.cfg.hourly_wage
    expected_brl = expected_eur * brl
    difference_eur = difference * client.cfg.hourly_wage
    difference_brl = difference_eur * brl

    output_result = (
        ("Hours to do: {0:.2f}h ({1:.2f} days) -> €{2:.2f} - R${3:.2f}".format(expected, expected/client.cfg.work_hours_per_day, expected_eur, expected_brl)) + "\r\n" +
        ("Hours worked: {0:.2f}h ({1:.2f} days) -> €{2:.2f} - R${3:.2f}".format(actual, actual/client.cfg.work_hours_per_day, actual_eur, actual_brl)) + "\r\n" +
        ("Difference: {0:.2f}h ({1:.2f} days) -> €{2:.2f} - R${3:.2f}".format(difference, difference/client.cfg.work_hours_per_day, difference_eur, difference_brl)) + "\r\n" +
        f"1€ = R${brl} on {brl_update_date}"
    )
    print("*"*60)
    print(output_result)
    print("*"*60)

    if args.command == 'lastmonth':
        email_message = (
            f"Bonjour {client.cfg.boss_name}," + "\n" +
            "Je vous envoie le total du mois de <month>." + "\n" +
            "Prévu pour le mois:  {0:.2f}h ({1:.2f} jours)".format(expected, expected/client.cfg.work_hours_per_day) + "\n" +
            "Total pour le mois:  {0:.2f}h ({1:.2f} jours)".format(actual, actual/client.cfg.work_hours_per_day) + "\n" +
            "Total:  {0:.2f} hrs x {1:.1f} = €{2:.2f}".format(actual, client.cfg.hourly_wage, actual * client.cfg.hourly_wage) + "\n" +
            "\n" +
            "Quel jour de cette semaine vous pouvez fair le virement?" + "\n" +
            "Dans le même jour je vais générer le document fiscale en considerant de la cotation du jour forni par transferwise." + "\n" +
            "\n" +
            "Je vous souhaite une bonne journée."
        )
        print("*"*80)
        print("Rapport des heures - <month>")
        print("*"*40)
        print(email_message)
        print("*"*80)

    print(f"Running time entry: {'Yes' if running else 'No'}")
    if args.notify and difference >= 0 and running:
        from gi import require_version
        require_version('Notify', '0.7')
        from gi.repository import Notify
        Notify.init("Toggle Notifier")
        notification=Notify.Notification.new(
            f'Time to stop working (+{difference:.2f}h)',
            ('-' * 112) + "\r\n" + output_result,
            "dialog-information"
        )
        notification.set_timeout(0) # persist
        notification.show ()

    if args.uses_notify_send and difference >= 0 and running:
        import os
        title = f'Time to stop working (+{difference:.2f}h)'
        os.system(
            "notify-send \"" + title + "\" " + " \"" +
            output_result + "\""
        )
    

