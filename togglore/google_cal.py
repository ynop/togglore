from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from utils import get_weekends, annotate_weekday_name, reduce, append_annotate, deflate


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class Calendar(object):
    service = None

    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def get_holidays(self):
        resources = {
            'en.christian#holiday@group.v.calendar.google.com',
            'en.austrian#holiday@group.v.calendar.google.com',
            'de.austrian#holiday@group.v.calendar.google.com',
        }

        holidays = []
        for cal in resources:
            events_result = self.service.events().list(
                calendarId=cal,
                timeMin=from_date,
                # timeMax=to_date,
                maxResults=2500,
                # orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            for event in events:
                holidays.append(deflate(event))
        import ipdb; ipdb.set_trace()
        return reduce(*holidays)

    def get_events_by_name(self, name, from_date=None, to_date=None):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat()
        events_result = self.service.events().list(
            q=name,
            calendarId='ubergrape.com_450doe35u9mtlhfuuqkr462c6o@group.calendar.google.com',
            #timeMin=from_date,
            #timeMax=to_date,
            maxResults=2500,
            #orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        return reduce(events)


if __name__ == '__main__':
    from_date = datetime.date(2017, 8, 1)
    cal = Calendar()

    weekends = annotate_weekday_name(get_weekends())
    holidays = cal.get_holidays()

    empl = [
        {'chris', 'christoph'},
        {'victor'},
        {'melanie'},
        {'stefan'},
        {'riccardo'},
        {'blerta'},
        {'carina'},
        {'ivan'},
        {'sandor'},
        {'oleh'},
        {'felix'},
        {'ron'},
        {'lukas', 'luke'},
        {'daniele'},
    ]

    vacations = {}
    for name in empl:
        f_name = None
        empl_vac = {}
        for nik in name:
            if not f_name:
                f_name = nik
            annotate = f'{nik} vacation'
            empl_vac = cal.get_events_by_name(f'{nik} vacation', from_date)
            empl_vac.update(cal.get_events_by_name(f'{nik} holiday', from_date))
            break

        vacations[f_name] = empl_vac
        vacations[f_name] = append_annotate(vacations[f_name], weekends, holidays)

        for empl, vacation in vacations:
            print('__________________________________________-')
            print(f'{empl}\'s vacations:')
            print(vacations)

        print(vacations)
