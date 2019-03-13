#!/usr/bin/python3

import oncampus
import html

PRESERVE_BOLD_ITALIC=True

def sanitizeString(s):
    sanitized = html.unescape(s).replace('<br />', '\n')
    if PRESERVE_BOLD_ITALIC:
        return sanitized.replace('<b>', '\x1b[1m')\
                .replace('</b>', '\x1b[22m')\
                .replace('<i>', '\x1b[3m')\
                .replace('</i>', '\x1b[23m')\
                .replace('<br />', '\n')
    else:
        return sanitized
