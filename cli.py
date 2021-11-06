#!/usr/bin/python3

import html
import shutil
import textwrap

import oncampus

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

# name, lamb, wrap, minLen
assignmentColumns = {
    'className': ('Class', lambda a: getClassDisplayName(a.className), False, None),
    'title': ('Assignment', lambda a: sanitizeString(a.title, True), True, 20),
    'status': ('Status', lambda a: statusMap[a.status], False, None)
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

# TODO: behaves badly when ANSI codes are involved
def displayTable(data, columns):
    lens = []
    for name, lamb, wrap, minLen in columns:
        if wrap:
            lens.append(-minLen)
        else:
            maxLen = max(len(name), max(map(lambda d: len(lamb(d)), data)))
            lens.append(maxLen)

    definiteLens = [l for l in lens if l >= 0]
    widthRemaining = shutil.get_terminal_size().columns\
            - sum(definiteLens)\
            - (3 * len(lens) + 1)\
            - sum([-l for l in lens if l < 0])

    if widthRemaining < 0:
        # use minimum length for wrapping columns
        lens = map(abs, lens)
    else:
        # evenly distribute remaining space
        amountToAdd = widthRemaining // (len(lens) - len(definiteLens))
        lens = map(lambda l: -l + amountToAdd if l < 0 else l, lens)

    lens = list(lens)

    # header
    print(f'+{"-" * (sum(lens) + 3 * len(columns) - 1)}+')
    print('|', end='')
    for i, (name, *_) in enumerate(columns):
        print(f' {name.ljust(lens[i])} |', end='')
    print('\n|', end='')
    for l in lens[:-1]:
        print(f'-{"-" * l}-+', end='')
    print(f'-{"-" * lens[-1]}-|')

    # data
    for d in data:
        wrappedLines = {}
        for i, (_, lamb, *_) in [(i, c) for i, c in enumerate(columns) if c[2]]:
            wrappedLines[i] = textwrap.wrap(lamb(d), lens[i])

        for i in range(max(map(len, wrappedLines.values()))):
            print('|', end='')

            for j, (_, lamb, *_) in enumerate(columns):
                if j in wrappedLines:
                    val = wrappedLines[j][i] if i < len(wrappedLines[j]) else ''
                elif i == 0:
                    val = lamb(d)
                else:
                    val = ''
                print(f' {val.ljust(lens[j])} |', end='')

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
