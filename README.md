oncampus
========

This is a Python library and CLI for accessing Blackbaud's onCampus service (typically \*.myschoolapp.com) that I started working on in 2019. I likely won't work on this any more, since I no longer go to a school that uses onCampus, but you're welcome to look at the code and potentially adapt it for something else.

Basic usage (from inside the `oncampus` folder):

```py
from datetime import date

import oncampus, cli

s = oncampus.getSession('YOUR_DOMAIN', 'YOUR_USERNAME', 'YOUR_PASSWORD')

a = oncampus.getAssignments(s, startDate=date.today(), endDate=date.today(), filterMode=oncampus.FILTER_DUE)

cli.showAssignments(a)
```

This shows assignments that are due today.
