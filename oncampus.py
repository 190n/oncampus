#!/usr/bin/python3

import requests
import simplejson
from datetime import datetime

USER_AGENT = 'OnCampus CLI v0.0.0'

FILTER_ASSIGNED = 0
FILTER_ACTIVE = 2
FILTER_DUE = 1

class Assignment:
    STATUS_TODO = -1
    STATUS_IN_PROGRESS = 0
    STATUS_COMPLETED = 1
    STATUS_OVERDUE = 2
    STATUS_GRADED = 4
    STATUS_PAUSED = 6

    DATETIME_FORMAT = '%m/%d/%Y %I:%M %p'

    def __init__(self, data, domain):
        self.className = data['groupname']
        self._id = data['assignment_id']
        self.indexId = data['assignment_index_id']
        self.type = data['assignment_type']
        self.title = data['short_description']
        self.description = data['long_description']
        self.status = data['assignment_status']

        self.dateAssigned = datetime.strptime(data['date_assigned'], Assignment.DATETIME_FORMAT)
        self.dateDue = datetime.strptime(data['date_due'], Assignment.DATETIME_FORMAT)
        self.domain = domain
        self.url = f'https://{domain}/app/student#assignmentdetail/{self._id}/{self.indexId}/0/studentmyday--assignment-center'

    def changeStatus(self, newStatus, token):
        url = f'https://{self.domain}/api/assignment2/assignmentstatusupdate/?format=json&t={token}'
        json = {
            'assignmentIndexId': self.indexId,
            'assignmentStatus': newStatus
        }

        r = requests.post(url, json=json, headers = {'User-Agent': USER_AGENT})

        if r.status_code != 200:
            try:
                if r.json()['ErrorType'] == 'INVALID_AUTHORIZATION':
                    raise Exception('Invalid token')
            except simplejson.JSONDecodeError:
                raise requests.HTTPError(r.text)

        self.status = newStatus
        return True

def getToken(domain, username, password):
    url = f'https://{domain}/api/SignIn'
    json = {'Username': username, 'Password': password}
    r = requests.post(url, json=json, headers = {'User-Agent': USER_AGENT})
    
    if r.status_code != 200:
        raise requests.HTTPError(r.text)
    else:
        try:
            return r.cookies['t']
        except KeyError:
            try:
                if not r.json()['LoginSuccessful']:
                    raise Exception(f'Incorrect password for user {username}')
                else:
                    raise Exception(f'Failed to log in as user {username}')
            except simplejson.JSONDecodeError:
                raise Exception(f'Failed to log in as user {username}')

# formats a Python date object as MM/DD/YYYY which the API expects
def formatDate(d):
    return d.strftime('%m/%d/%Y')

def parseAssignmentData(data, domain):
    return [Assignment(i, domain) for i in data]

def getAssignments(filter, startDate, endDate, domain, token):
    url = f'https://{domain}/api/DataDirect/AssignmentCenterAssignments'
    url += f'?format=json&persona=2&filter={filter}&dateStart={formatDate(startDate)}&dateEnd={formatDate(endDate)}&t={token}'

    r = requests.get(url, headers = {'User-Agent': USER_AGENT})

    try:
        json = r.json()
        if 'Error' in json:
            if json['ErrorType'] == 'INVALID_AUTHORIZATION':
                raise Exception('Invalid token')
            else:
                raise Exception(json['Error'])

        return parseAssignmentData(json, domain)
    except simplejson.errors.JSONDecodeError:
        raise ValueError('Got non-JSON response from API')


