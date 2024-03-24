import datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates


def date_histogram(dt: list[datetime]):
    dates: list[datetime.date] = [dt1.date() for dt1 in dt]
    plt.figure(figsize=(10, 6))
    plt.hist(dates, bins=len(set(dates)), color='skyblue', edgecolor='black', align='mid')
    # Format the x-axis to show dates
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gcf().autofmt_xdate()  # Rotate date labels
    plt.xlabel('Date')
    plt.ylabel('Number of records')
    plt.title('Histogram by Date')
    plt.tight_layout()  # Adjust layout to not cut off labels
    plt.show()


def hour_histogram(dt: list[datetime]):
    hours: list[int] = [dt1.hour for dt1 in dt]
    plt.figure(figsize=(10, 6))
    plt.hist(hours, bins=range(24), color='skyblue', edgecolor='black', align='left')
    plt.xticks(range(24))
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of records')
    plt.title('Histogram by Hour of Day')
    plt.grid(axis='y', alpha=0.75)
    plt.show()
