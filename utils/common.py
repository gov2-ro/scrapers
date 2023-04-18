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

def base_headers(which='headers1'):
  zeheaders = { "headers1": {
        'authority': 'monitoruloficial.ro',
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'PHPSESSID=f2a8g1t1f8oldgi3pntsopgpjk',
        'origin': 'https://monitoruloficial.ro',
        'referer': 'https://monitoruloficial.ro/e-monitor/',
        'sec-ch-ua': '"Chromium";v="112", "Brave";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    },
    "headers2": {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/111.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'origin': 'https://monitoruloficial.ro',
        'Referer': 'https://monitoruloficial.ro/e-monitor/',
        'Connection': 'keep-alive',
        'Cookie': 'PHPSESSID=s19e89glsqse9en1m0db4a4l53',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'TE': 'trailers'
    }
  }  
  if which in zeheaders:
    return zeheaders[which]
  else:
     return zeheaders['headers1']


 