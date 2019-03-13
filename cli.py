#!/usr/bin/python3

import oncampus
import html

PRESERVE_BOLD_ITALIC=True

classMap = {}

statusMap = {
    oncampus.Assignment.STATUS_TODO: 'To Do',
    oncampus.Assignment.STATUS_IN_PROGRESS: 'In Progress',
    oncampus.Assignment.STATUS_COMPLETED: 'Completed',
    oncampus.Assignment.STATUS_OVERDUE: 'Overdue',
    oncampus.Assignment.STATUS_GRADED: 'Graded',
    oncampus.Assignment.STATUS_PAUSED: 'Paused'
}

assignmentColumns = {
    'className': ('Class', lambda a: getClassDisplayName(a.className)),
    'title': ('Assignment', lambda a: sanitizeString(a.title, True)),
    'status': ('Status', lambda a: statusMap[a.status])
}

statusMaxLength = max(6, max(map(len, statusMap.values())))

def sanitizeString(s, stripNewlines=False):
    sanitized = html.unescape(s).replace('<br />', '\n')
    if PRESERVE_BOLD_ITALIC:
        sanitized = sanitized.replace('<b>', '\x1b[1m')\
                .replace('</b>', '\x1b[22m')\
                .replace('<i>', '\x1b[3m')\
                .replace('</i>', '\x1b[23m')\
                .replace('<br />', '\n')
    if stripNewlines:
        sanitized = sanitized.replace('\n', '')

    return sanitized

def getClassDisplayName(className):
    if className in classMap:
        return classMap[className]
    else:
        return className

# TODO: doesn't handle multi-line data!!!
def displayTable(data, columns):
    lens = []
    for name, lamb in columns:
        maxLen = max(len(name), max(map(lambda d: len(lamb(d)), data)))
        lens.append(maxLen)

    # header
    print(f'+{"-" * (sum(lens) + 3 * len(columns) - 1)}+')
    print('|', end='')
    for i, (name, _) in enumerate(columns):
        print(f' {name.ljust(lens[i])} |', end='')
    print('\n|', end='')
    for l in lens[:-1]:
        print(f'-{"-" * l}-+', end='')
    print(f'-{"-" * lens[-1]}-|')

    # data
    for d in data:
        print('|', end='')
        for i, (_, lamb) in enumerate(columns):
            print(f' {lamb(d).ljust(lens[i])} |', end='')
        print('\n', end='')

    # footer
    print(f'+{"-" * (sum(lens) + 3 * len(columns) - 1)}+')

# def showAssignments(assignments):
#     classNameWidth = max(5, max(map(lambda a: len(getClassDisplayName(a.className)), assignments)))
#     titleWidth = max(10, max(map(lambda a: len(a.title), assignments)))

#     print(f'+{"-" * (classNameWidth + titleWidth + statusMaxLength + 10)}+')

#     print(f'| {"Class".ljust(classNameWidth)} | {"Title".ljust(titleWidth)} | {"Status".ljust(statusMaxLength)} |')
#     print(f'|-{"-" * classNameWidth}-+-{"-" * titleWidth}-+-{"-" * statusMaxLength}-|')

#     for a in assignments:
#         showAssignment(a, classNameWidth, titleWidth)

#     print(f'+{"-" * (classNameWidth + titleWidth + statusMaxLength + 10)}+')

def showAssignments(assignments):
    cols = ('className', 'title', 'status')
    displayTable(assignments, [assignmentColumns[c] for c in cols])
