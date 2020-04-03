import urllib
import urllib.request
import urllib.parse
import base64
import json


class TogglClient(object):
    def __init__(self, api_token, user_id, workspace, project):
        self.api_token = api_token
        self.user_id = user_id
        self.workspace = workspace
        self.project = project
        self.headers = {}
        self.__init_headers()

    def __init_headers(self):
        auth_header = self.api_token + ":" + "api_token"
        auth_header = "Basic {}".format(base64.b64encode(bytes(auth_header, "utf-8")).decode("ascii"))
        self.headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "togglore",
        }

    def request(self, endpoint, parameters=None):
        if parameters is not None:
            url = '{}?{}'.format(endpoint, urllib.parse.urlencode(parameters))
        else:
            url = endpoint

        req = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(req).read()

        return json.loads(response.decode('utf8'))

    def time_entries(self, date_range):
        entries = []

        total = 1
        per_page = 0
        current_page = 0

        while current_page * per_page < total:
            current_page += 1
            url = self._get_toggl_url(
                workspace_id=self.workspace,
                project_id=self.project,
                since=date_range.start.isoformat(),
                until=date_range.end.isoformat(),
                user_agent='togglore',
                page=current_page,
            )
            response = self.request(url)
            total = response['total_count']
            per_page = response['per_page']
            for time in response['data']:
                if str(time['uid']) == self.user_id:
                    entries.append(time)

        return entries

    def running_time_entry(self):
        entry = None
        url = "https://www.toggl.com/api/v8/time_entries/current"
        response = self.request(url)
        if (str(response['data']['wid']) == self.workspace and
           str(response['data']['uid']) == self.user_id and
           str(response['data']['pid']) == self.project):
            entry = response['data']
        return entry


    def _get_toggl_url(self, workspace_id, project_id, since, until, user_agent, page):
        url = (
            f"https://toggl.com/reports/api/v2/details?" +
            f"workspace_id={workspace_id}&"
            f"project_ids={project_id}&"
            f"since={since}&"
            f"until={until}&"
            f"user_agent={user_agent}&"
            f"page={page}"
        )
        return url
