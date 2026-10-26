import shutil
import csv
from datetime import datetime, timedelta
from os.path import exists
from gentraffic import gentraffic
from koop_db import traffic_week_order, traffic_week_of_date
from google_tools.update_traffic_log import update_traffic_log
from google_tools.send_results import send_results
from xfile import xfile
from update_dad import update_dad
from extract_lengths_and_send_gmail import extract_lengths_and_send_gmail 

on_prod = False
if exists('/mnt/DAD/DAD/Files/CUTS.DBF'):
    on_prod = True
    prefix='/home/debian/gentraffic/'
else:
    prefix='./'

def find_start_day(csv_file):
    with open(csv_file, 'r') as file:
        traffic_rows = list(csv.reader(file))

    week_of_date = traffic_week_of_date(traffic_rows)
    if week_of_date is None:
        return None

    # Calculate the current date without the time component
    current_date = datetime.now().date()

    # If "week of" is in the future, start on the first day of the traffic week
    if current_date < week_of_date:
        return traffic_week_order(traffic_rows)[0].upper()

    # Calculate the difference in days from "week of" to current date
    days_diff = (current_date - week_of_date).days

    # If today is within the "week of" period but not the last day, find the next valid update day
    if 0 <= days_diff < 6:
        next_valid_day = current_date + timedelta(days=1)  # The day after the current day
        next_valid_day_name = next_valid_day.strftime("%A").upper()  # Get the day name in uppercase
        return next_valid_day_name

    # If the current day is the last day of the "week of" period or the entire week is in the past, return None
    return None

def auto_gentraffic():
    print("launching auto_gentraffic")
    if update_traffic_log():
        print("Passed traffic log test")
        startday = find_start_day(prefix+"traffic.csv")
        print("start day = ", startday)
        if startday:
            shutil.move(prefix+"traffic.csv", prefix+"inputfiles/traffic.csv",copy_function=shutil.copy)
            if gentraffic(startday):
                print("Finished gentraffic phase")
                xfile()
                print("Updating DAD with startday", startday)
                update_dad(startday)
                if on_prod:
                    send_results()
                    # not any more extract_lengths_and_send_gmail()
                print("\nAll Programs Finished!!\n")
                current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
                # GROK shutil.make_archive(f'../gt_{current_datetime}', 'zip', '..', 'gentraffic')
                return True
    return False

if __name__ == '__main__':
    print("calling auto_gentraffic directly")
    if not auto_gentraffic():
        print("auto_gentraffic finished with nothing to do!!!!")
