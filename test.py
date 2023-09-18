from datetime import date, timedelta

# def allsundays(year):
#     d = date(year, 1, 1)                    # January 1st
#     d += timedelta(days = 6 - d.weekday())  # First Sunday
#     while d.year == year:
#         yield d
#         d += timedelta(days = 7)
#
# for d in allsundays(2010):
#     print(d)

date_1 = date(2023, 7, 1)
while date_1.weekday() != 0 :
    date_1 += timedelta(days = 1)
print(date_1)
print(date_1.weekday())
date_2 = date(2024, 6, 30)
date_1 += timedelta(days = 6 - date_1.weekday())
delta = timedelta(days=7)
while date_1 <= date_2:
    print(date_1.strftime("%Y-%m-%d"))
    date_1 += delta