#!/usr/bin/env python3

import os
from datetime import date, datetime

today = date.today()
print('Checking db backups for removal: {}'.format(today))

root = '/data/backups'
for fn in os.listdir(root):

    if '.sql.gz' not in fn:
        continue

    d1 = datetime.strptime(fn, 'hawc-%Y-%m-%dT%H_%M.sql.gz').date()
    days = (today - d1).days

    if days <= 14:
        # keep all <= 14 days
        keep = True
    elif days <= 90:
        # keep one weekly for 3 months (or first of month)
        keep = (d1.day == 1 or d1.weekday() == 0)
    else:
        # keep only the first of the month
        keep = (d1.day == 1)

    if not keep:
        fn = os.path.join(root, fn)
        print('Removing %s' % fn)
        os.system('rm {}'.format(fn))

print('db backup removal complete')
