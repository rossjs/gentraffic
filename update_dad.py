from koop_db import read_traffic, traffic_week_order, traffic_week_of_date, cli_startday
from verify_utils import getdates
from datetime import datetime
from os.path import exists
from sys import argv
import shutil

if exists('/mnt/DAD/DAD/Files/CUTS.DBF'):
    prefix='/home/debian/gentraffic/'
else:
	prefix='./'

def update_dad(startday):
    on_prod = False
    if exists('/mnt/DAD/DAD/Files/CUTS.DBF'):
        print("\n on production!!!")
        on_prod = True

    ascii_traffic = read_traffic()
    weekof_date = traffic_week_of_date(ascii_traffic)
    if weekof_date is None:
        print("\nError! ==> No 'Week of' date found in the traffic CSV.\n")
        return False
    weekof_dt = datetime.combine(weekof_date, datetime.min.time())


    dates = getdates(ascii_traffic)
    #print("This week's AUTO files are:",dates,'\n')
    # DAD day-file names (e.g. WEDNESDA), in the CSV's column order
    week = [day.upper()[:8] for day in traffic_week_order(ascii_traffic)]

    # get current datetime
    # there was a bug here where it was always getting gmt time.  can't remember how it was fixed
    dt_now = datetime.now()
    print("\nToday's date is:", dt_now)

    # get weekday name
    #print('\nToday is ', dt_now.strftime('%A'),dt_now.month,dt_now.day)
    #print('Month/Day is ', str(dt_now.month).zfill(2)+str(dt_now.day).zfill(2),"\n")


    if weekof_dt < dt_now and startday.upper()[:3] == week[0][:3]:
        print('\nError! ==> Refusing to autocopy into the past.\n')
        return False
        
    started = False

    for date in dates:
        day = week.pop(0)
        if day in startday.upper() or startday.upper() in day:
            started = True
        if not started:
            continue
        auto_file = prefix+"outputfiles/"+date+"AUTO.DBF"
        day_file = prefix+"outputfiles/"+day+".DBF"
        shutil.copy(day_file,auto_file)
        if on_prod:
            shutil.copy(auto_file,"/mnt/DAD/DAD/Files/PLAYLIST")
        
        print("Updated",auto_file)
    print("\nUpdateDad Finished! Traffic successfully copied to mapped Drive.\n")

if __name__ == "__main__":
    update_dad(cli_startday(argv))
