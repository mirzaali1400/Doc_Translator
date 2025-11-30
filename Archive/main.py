import datetime
import Gap as mygap
import time


tic = datetime.datetime.now()

mygap.translatePDF_to_Word("input/IEC 62443-3-3 2013-13-15.pdf")

toc = datetime.datetime.now()
duration = toc - tic
duraton_seconds = duration.total_seconds()
minute= divmod(duraton_seconds,60)
print("Duration : ",duration)
print(f"Duration in minute : {int(minute[0])}:{int(minute[1])}")

