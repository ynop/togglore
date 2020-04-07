import argparse
import datetime

import togglore
from togglore import utils


def main():
    parser = argparse.ArgumentParser(description='Tool for toggle to calculate over/undertime.')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    parser_range = subparsers.add_parser('range', help='range help')
    parser_range.add_argument('from_date', help='startdate, e.g. 30.08.2016')
    parser_range.add_argument('to_date', help='enddate, e.g. 12.10.2016')

    parser_updatecotation = subparsers.add_parser('updatecotation', help='updatecotation help')

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

    if args.command == 'updatecotation':
        client.cfg.update_eur_value(client.config_path)
        brl = float(client.cfg.eur_to_brl['value'])
        brl_update_date = client.cfg.eur_to_brl['date']
        print(f"* EUR value updated to {brl:.3f} BRL on {brl_update_date}")
        return

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
        "Hours to do:\t{0:6.2f}{1} ({2:5.2f} days) -> €{3:7.2f} | R$ {4:4.0f}".format(
            expected if abs(expected) >= 1 else expected * 60,
            " h" if abs(expected) >= 1 else " min",
            expected/client.cfg.work_hours_per_day,
            expected_eur,
            expected_brl
        ) + "\r\n" +
        "Hours worked:\t{0:6.2f}{1} ({2:5.2f} days) -> €{3:7.2f} | R$ {4:4.0f}".format(
            actual if abs(actual) >= 1 else actual * 60,
            " h" if abs(actual) >= 1 else " min",
            actual/client.cfg.work_hours_per_day,
            actual_eur,
            actual_brl
        ) + "\r\n" +
        "Difference:\t{0:6.2f}{1} ({2:5.2f} days) -> €{3:7.2f} | R$ {4:4.0f}".format(
            difference if abs(difference) >= 1 else difference * 60,
            " h" if abs(difference) >= 1 else " min",
            difference/client.cfg.work_hours_per_day,
            abs(difference_eur),
            abs(difference_brl)
        ) + "\r\n" +
        "-" * 60 + "\r\n" +
        f"Cotation on {brl_update_date}: 1 EUR = {brl:.3f} BRL"
    )

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
        print("-"*45)
        print(email_message)
        print("*"*80)
    elif args.command == 'lastweek':
        expected_end_of_month = client.time_calculator.time_to_work_in_range(
            utils.DateRange.this_month()
        )
        date_range = utils.DateRange.last_week()
        actual_hours = int(actual)
        actual_minutes_float = (actual - actual_hours) * 60
        actual_minutes = int(actual_minutes_float)
        actual_seconds = int((actual_minutes_float - actual_minutes) * 60)
        # Email template
        email_message = (
            f"Bonjour {client.cfg.boss_name}," + "\n" +
            "Pour info je vous envoie la quantité des heures que j'ai fait la semaine dernière." + "\n\n" +
            "Total (Semaine) : {}:{}:{} ({:.2f} hrs)".format(
                actual_hours,
                actual_minutes,
                actual_seconds,
                actual,
            ) + "\n" +
            "Balance (Semaine) : {}:{} ({:.2f} hrs)".format(
                int(difference),
                int((difference - int(difference)) * 60),
                difference,
            ) + "\n" +
            "Total prévu pour le mois : {0:.2f}h ({1:.0f} jours)".format(
                expected_end_of_month, expected_end_of_month/client.cfg.work_hours_per_day
            ) + "\n\n" +
            "Cordialement,\nItalo Gustavo Sampaio Fernandes"
        )
        print("*"*80)
        print("Rapport des heures - Semaine {start} à {end}".format(
            start=date_range.start.strftime("%d/%m"),
            end=date_range.end.strftime("%d/%m")
        ))
        print("-"*45)
        print(email_message)
        print("*"*80)
    elif args.command == 'thismonth':
        expected_end_of_month = client.time_calculator.time_to_work_in_range(
            utils.DateRange.this_month()
        )
        output_result = output_result + (
            "\r\n" +
            "Total: {0:.2f} hrs x {1:.1f}€ (R$ {2:.1f}) = €{3:.2f} | R$ {4:.0f}".format(
                expected_end_of_month,
                client.cfg.hourly_wage,
                client.cfg.hourly_wage * brl,
                expected_end_of_month * client.cfg.hourly_wage,
                expected_end_of_month * client.cfg.hourly_wage * brl,
            )
        )
        if args.untiltoday:
            actual_today, expected_today, running_today = client.diff(utils.DateRange.today(), include_running=True)
            output_result = output_result + (
                "\r\n" +
                "-" * 60 + "\r\n"
            )
            if difference <= 0:
                finish_prevision = (
                    datetime.datetime.now() +
                    datetime.timedelta(hours=-difference)
                ).strftime("%H:%M")
                output_result = output_result + (
                    f"Finish prevision ({-difference:.2f}h): {finish_prevision}" + "\r\n" +
                    "-" * 60 + "\r\n"
                )
            output_result = output_result + (
                "Today: " + f"{actual_today:.2f}h / {expected-actual+actual_today:.2f}h" + "\r\n" +
                "{0:3.0f}%".format(100*actual_today/(expected-actual+actual_today)) + " " + "[" + "=" * int(actual_today*54/(expected-actual+actual_today)) + "-" * int(-(difference)*54/(expected-actual+actual_today)) + "]" + "\r\n" +
                "This Month: " + f"{actual/client.cfg.work_hours_per_day:.2f} / {(expected_end_of_month/client.cfg.work_hours_per_day):.0f} days        -       " + f"R$ {actual_brl:.0f} / R$ {(expected_end_of_month * client.cfg.hourly_wage * brl):.0f}" + "\r\n" +
                "{0:3.0f}%".format(100*actual/expected_end_of_month) + " " + "[" + "=" * int(actual*54/expected_end_of_month) + "-" * int(-(actual-expected_end_of_month)*54/expected_end_of_month) + "]"
            )
    elif args.command == 'today':
        expected_end_of_month = client.time_calculator.time_to_work_in_range(
            utils.DateRange.this_month()
        )
        output_result = output_result + (
            "\r\n" +
            "Total: {0:.2f} hrs x {1:.1f}€ (R$ {2:.1f}) = €{3:.2f} | R$ {4:.0f}".format(
                expected_end_of_month,
                client.cfg.hourly_wage,
                client.cfg.hourly_wage * brl,
                expected_end_of_month * client.cfg.hourly_wage,
                expected_end_of_month * client.cfg.hourly_wage * brl,
            )
        )
        output_result = output_result + (
            "\r\n" +
            "-" * 60 + "\r\n"
        )
        if difference <= 0:
            finish_prevision = (
                datetime.datetime.now() +
                datetime.timedelta(hours=-difference)
            ).strftime("%H:%M")
            output_result = output_result + (
                f"Finish prevision ({-difference:.2f}h): {finish_prevision}" + "\r\n" +
                "-" * 60 + "\r\n"
            )
        output_result=output_result + (
            "Today: " + f"{actual:.2f}h / {expected:.2f}h" + "\r\n" +
            "{0:3.0f}%".format(100*actual/expected) + " " + "[" + "=" * int(actual*54/expected) + "-" * int(-difference*54/expected) + "]"
        )


    print("*"*60)
    print(output_result)
    print("*"*60)

    print(f"Working now: {'Yes' if running else 'No'}")
    if args.notify and difference >= 0 and running:
        from gi import require_version
        require_version('Notify', '0.7')
        from gi.repository import Notify
        Notify.init("Toggle Notifier")
        notification=Notify.Notification.new(
            'Time to stop working (+{0:.2f}{1})'.format(
                difference if abs(difference) >= 1 else difference * 60,
                " h" if abs(difference) >= 1 else " min",
            ),
            ('-' * 112) + "\r\n" + output_result,
            "dialog-information"
        )
        notification.set_timeout(Notify.EXPIRES_NEVER)  # persist
        notification.set_urgency(Notify.Urgency.CRITICAL)  # persist
        notification.show ()

    if args.uses_notify_send and difference >= 0 and running:
        import os
        title = 'Time to stop working (+{0:.2f}{1})'.format(
                difference if abs(difference) >= 1 else difference * 60,
                " h" if abs(difference) >= 1 else " min",
        )
        os.system(
            "notify-send \"" + title + "\" " + " \"" +
            output_result + "\""
        )
    

if __name__ == '__main__':
    main()
