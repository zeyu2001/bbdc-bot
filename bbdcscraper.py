import os
import re
import requests
from datetime import datetime

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# BBDC Blocked Heroku's IP Range
PROXY_DICT = {
              "http"  : os.environ.get('FIXIE_URL', ''),
              "https" : os.environ.get('FIXIE_URL', '')
            }

LOGIN_URL = 'http://www.bbdc.sg/bbdc/bbdc_web/header2.asp'
BOOKING_URL = 'http://www.bbdc.sg/bbdc/b-3c-pLessonBooking1.asp'

DETAILS_REGEX = r'doTooltipV\(event,0, "(.+?)","(.+?)","(.+?)","(.+?)","(.+?)"\);'

class BBDCScraper:

    def __init__(self):
        self.acct_id = None
        self.session = requests.Session()

    def login(self, username, password, acct_id):

        print("[INFO] Attempting login.")

        data = {
            'txtNRIC': username,
            'txtpassword': password,
            'ca': 'true',
            'btnLogin': 'ACCESS+TO+BOOKING+SYSTEM'
        }

        r = self.session.post(LOGIN_URL, data=data, proxies=PROXY_DICT, allow_redirects=False)

        if "*Invalid user id or password. Please try again." in r.text:
            raise RuntimeError("LOGIN ERROR: Unable to login, please check credentials.")

        self.acct_id = acct_id

        print("[INFO] Logged in successfully.")

    def get_available_slots(self, months, sessions, days):

        current_month = datetime.now().month
        current_year = datetime.now().year

        months_lst = []

        for offset in months:
            month_num, year_num = current_month + offset - 1, current_year

            # Next year
            if month_num >= 12:
                year_num += 1
                month_num %= 12

            months_lst.append(f'{MONTHS[month_num]}/{year_num}')

        data = {
            'accId': self.acct_id,
            'Month': months_lst,
            'Session': [i for i in range(1, 9)],
            'Day': [i for i in range(1, 8)],
            'defPLVenue': '1',
            'optVenue': '1'
        }
        r = self.session.post(BOOKING_URL, data=data, proxies=PROXY_DICT)
        slots = re.findall(DETAILS_REGEX, r.text)

        results = []
        for slot in slots:

            date, session, starttime, endtime, venue = slot

            results.append({
                'date': date,
                'session': session,
                'starttime': starttime,
                'endtime': endtime,
                'venue': venue
            })

        return results
