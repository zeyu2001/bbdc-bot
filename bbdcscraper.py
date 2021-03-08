import os

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Chromedriver
CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH")
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

# Login Page
BBDC_URL = "https://info.bbdc.sg/members-login/"
USERNAME_FIELD_ID = "txtNRIC"
PWD_FIELD_ID = 'txtPassword'
LOGIN_BTN_ID = 'btnLogin'
MAINFRAME_URL = "http://www.bbdc.sg/bbdc/b-mainframe.asp"


class BBDCScraper:

    def __init__(self):
        self.opts = Options()
        self.opts.add_argument('--headless')    # Operating in headless mode
        self.opts.add_argument('--disable-gpu')
        self.opts.add_argument("--disable-dev-shm-usage")
        self.opts.add_argument("--no-sandbox")
        self.opts.add_argument("--incognito")
        self.opts.add_argument(f"user-agent={USER_AGENT}")
        self.opts.add_argument("window-size=1400,600")
        self.opts.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        self.browser = Chrome(CHROMEDRIVER_PATH, options=self.opts)

    def login(self, username, password):
        self.browser.get(BBDC_URL)
        wait = WebDriverWait(self.browser, 30)
        wait.until(EC.visibility_of_element_located((By.ID, USERNAME_FIELD_ID)))

        username_field = self.browser.find_element_by_id(USERNAME_FIELD_ID)
        username_field.send_keys(username)

        password_field = self.browser.find_element_by_id(PWD_FIELD_ID)
        password_field.send_keys(password)

        login_btn = self.browser.find_element_by_name(LOGIN_BTN_ID)
        login_btn.click()

        if not self.browser.current_url == MAINFRAME_URL:
            raise RuntimeError("LOGIN ERROR: Unable to login, please check credentials.")

    def get_available_slots(self, months, sessions, days):

        if not self.browser.current_url == MAINFRAME_URL:
            raise RuntimeError("URL ERROR: Incorrect URL, please login first.")

        else:
            # Switching to Left Frame and accessing element by text
            self.browser.switch_to.default_content()
            frame = self.browser.find_element_by_name('leftFrame')
            self.browser.switch_to.frame(frame)
            nonFixedInstructor = self.browser.find_element_by_link_text('Booking without Fixed Instructor')
            nonFixedInstructor.click()

            # Switching back to Main Frame and pressing 'I Accept'
            self.browser.switch_to.default_content()
            wait = WebDriverWait(self.browser, 30)
            wait.until(EC.frame_to_be_available_and_switch_to_it(self.browser.find_element_by_name('mainFrame')))
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "btn"))).click()

            # Choosing the desired slots
            month_checkboxes = self.browser.find_elements_by_id('checkMonth')
            for month in months:
                month_checkboxes[month].click()

            session_checkboxes = self.browser.find_elements_by_id('checkSes')
            for session in sessions:
                session_checkboxes[session].click()

            day_checkboxes = self.browser.find_elements_by_id('checkDay')
            for day in days:
                day_checkboxes[day].click()

            # Selecting Search
            self.browser.find_element_by_name('btnSearch').click()

            # Dismissing Prompt
            wait = WebDriverWait(self.browser, 30)

            try:
                wait.until(EC.alert_is_present())
                alert_obj = self.browser.switch_to.alert
                alert_obj.accept()

            except TimeoutException:
                print("[INFO] No alert present. Proceeding to view slots.")
            
            wait.until(EC.visibility_of_element_located((By.NAME, "tipDiv1")))

            results = []
            slots = self.browser.find_elements_by_name('slot')
            for slot in slots:
                td = slot.find_element_by_xpath('..')
                text = td.get_attribute('onmouseover').split(';')[0].replace('"', '')
                parts = text.split(',')

                date, session, starttime, endtime, venue = parts[2:]
                venue = venue[:-1]

                results.append({
                    'date': date,
                    'session': session,
                    'starttime': starttime,
                    'endtime': endtime,
                    'venue': venue
                })

            return results
