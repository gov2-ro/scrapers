import datetime

def generate_dates(start_date_str, end_date_str, format='%d.%m.%Y'):
    # Convert the start and end date strings to date objects
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Define a function to check if a date is a weekend
    def is_weekend(date):
        return date.weekday() in [5, 6]  # 5 is Saturday and 6 is Sunday

    # Generate the list of dates, excluding weekends, and format them
    date_list = [
        (start_date + datetime.timedelta(days=x)).strftime(format)
        for x in range((end_date - start_date).days + 1)
        if not is_weekend(start_date + datetime.timedelta(days=x))
    ]

    return date_list