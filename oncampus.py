#!/usr/bin/python3

from datetime import datetime
from collections import namedtuple

import requests
import simplejson

USER_AGENT = 'OnCampus CLI v0.0.0'

FILTER_ASSIGNED = 0
FILTER_ACTIVE = 2
FILTER_DUE = 1

SessionInfo = namedtuple('SessionInfo', ['domain', 'token', 'persona', 'classes'])

class Assignment:
    STATUS_TODO = -1
    STATUS_IN_PROGRESS = 0
    STATUS_COMPLETED = 1
    STATUS_OVERDUE = 2
    STATUS_GRADED = 4
    STATUS_PAUSED = 6

    DATETIME_FORMAT = '%m/%d/%Y %I:%M %p'

    def __init__(self, session, data):
        self.className = data['groupname']
        self.classId = data['section_id']

        for c in session.classes:
            if c._id == self.classId:
                self._class = c

        self._id = data['assignment_id']
        self.indexId = data['assignment_index_id']
        self.type = data['assignment_type']
        self.title = data['short_description']
        self.description = data['long_description']
        self.status = data['assignment_status']

        self.dateAssigned = datetime.strptime(data['date_assigned'], Assignment.DATETIME_FORMAT)
        self.dateDue = datetime.strptime(data['date_due'], Assignment.DATETIME_FORMAT)
        self.domain = session.domain
        self.url = f'https://{session.domain}/app/student#assignmentdetail/{self._id}/{self.indexId}/0/studentmyday--assignment-center'

    def changeStatus(self, session, newStatus):
        url = f'https://{self.domain}/api/assignment2/assignmentstatusupdate/?format=json&t={session.token}'
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

class ClassInfo:
    def __init__(self, data, domain):
        self.domain = domain

        self._id = data['CurrentSectionId']
        self.name = data['GroupName']
        self.instructor = data['OwnerName']
        self.category = data['Category']
        self.block = data['SectionBlock']

        self.url = f'https://{domain}/app/student#academicclass/{self._id}/0/bulletinboard'

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

def parseAssignmentData(session, data):
    return [Assignment(session, i) for i in data]

def getAssignments(s, **kwargs):
    url = f'https://{s.domain}/api/DataDirect/AssignmentCenterAssignments?format=json&persona={s.persona}&t={s.token}'
    if 'startDate' in kwargs:
        url += f'&dateStart={formatDate(kwargs["startDate"])}'
    if 'endDate' in kwargs:
        url += f'&dateEnd={formatDate(kwargs["endDate"])}'
    if 'filterMode' in kwargs:
        url += f'&filter={kwargs["filterMode"]}'
    if 'status' in kwargs:
        url += f'&statusList={",".join([str(s) for s in kwargs["status"]])}'
    if 'classes' in kwargs:
        url += f'&sectionList={",".join([c.sectionId for c in kwargs["classes"]])}'


    r = requests.get(url, headers = {'User-Agent': USER_AGENT})

    try:
        json = r.json()
        if 'Error' in json:
            if json['ErrorType'] == 'INVALID_AUTHORIZATION':
                raise Exception('Invalid token')
            else:
                raise Exception(json['Error'])

        return parseAssignmentData(s, json)
    except simplejson.errors.JSONDecodeError:
        raise ValueError('Got non-JSON response from API')

def getSession(domain, username, password):
    token = getToken(domain, username, password)
    url = f'https://{domain}/api/webapp/context?t={token}'
    r = requests.get(url, headers = {'User-Agent': USER_AGENT})

    json = r.json()

    if 'Personas' not in json or 'Groups' not in json:
        raise Exception('Failed to get needed info from API')

    for p in json['Personas']:
        if 'DefaultPersona' in p and p['DefaultPersona']:
            defaultPersona = p['Id']

    classes = [ClassInfo(g, domain) for g in json['Groups'] if 'CurrentEnrollment' in g and g['CurrentEnrollment']]

    return SessionInfo(domain, token, defaultPersona, classes)
