#!/usr/bin/env python
from os.path import isfile
from argparse import ArgumentParser
from sqlite3 import connect
from datetime import date, timedelta

ap = ArgumentParser(description="Reads Tachiyomi database and lists all series"
                    "which haven't been updated within specified time frame.")
ap.add_argument("-y", "--years", default=0, type=float)
ap.add_argument("-m", "--months", default=0, type=float)
ap.add_argument("-w", "--weeks", default=0, type=float)
ap.add_argument("-d", "--days", default=0, type=float)
args = ap.parse_args()

if not isfile("tachiyomi.db"):
    raise FileNotFoundError("database file (tachiyomi.db) not found")

db = connect("tachiyomi.db")
c = db.cursor()

manga = dict(c.execute("SELECT _id, title FROM mangas WHERE favorite=1")
             .fetchall())
print("You have a total of {0} manga!\n".format(len(manga)))
chaps = c.execute("SELECT manga_id, date_upload FROM chapters WHERE "
                  "manga_id IN ({0})".format(','.join('?' for _ in manga)),
                  list(manga))

chapterTimes = {}
for line in chaps:
    mangaId, value = line
    try:
        if chapterTimes[mangaId] < value:
            chapterTimes[mangaId] = value
    except KeyError:
        chapterTimes[mangaId] = value

db.close()

days = args.years * 365.25 + args.months * 30.4375 + args.days
lastDate = date.today() - timedelta(days=days, weeks=args.weeks)

print("Series that have not been updates since {0}:".format(lastDate))
for x in chapterTimes:
    if date.fromtimestamp(chapterTimes[x]/1000) < lastDate:
        print("> " + manga[x])
