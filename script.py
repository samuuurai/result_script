from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from PIL import Image
from pytesseract import image_to_string
import smtplib
from email.message import EmailMessage
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to send email with screenshot
def send_email(screenshot_path):
    msg = EmailMessage()
    msg['Subject'] = "RESULT OUT"
    msg['From'] = "your_gmail"
    msg['To'] = "your_gmail"

    with open(screenshot_path, 'rb') as f:
        data = f.read()

    msg.add_attachment(data, maintype='image', subtype='png', filename='result_screenshot.png')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("your_gmail", "your_gmail_app_password(https://support.google.com/mail/answer/185833?hl=en)")
        smtp.send_message(msg)

# Define a custom expected condition function to check if the desired text is present in the page source
def text_present_in_page_source(text):
    def inner(driver):
        return text in driver.page_source
    return inner

# Set up Firefox webdriver
service = Service(executable_path='(https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz) download and unzip to extract geckodriver executable and paste its directory here like /usr/bin/geckodriver')
options = Options()
options.add_argument('--profile-directory=qa17lsmr.sel')
firefox_profile = FirefoxProfile('qa17lsmr.sel')
options.profile = firefox_profile
options.add_argument("--headless") # comment this whole line out if you want to see the browser window opened by script
driver = webdriver.Firefox(service=service, options=options)

# Main loop to check for changes in the webpage
while True:
    try:
        driver.get('https://results.cbse.nic.in/')

#replace Class XII with Class X if you're in X, also replace ..Senior School..it should be Secondary School Examination (Class X) Results 2023

        if 'Senior School Certificate Examination (Class XII) Results 2024' in driver.page_source or 'Class XII Results 2024' in driver.page_source:
            send_email('image.png')
            if 'Class XII Results 2024' in driver.page_source:
                result_link = driver.find_element('partial link text','Senior School Certificate Examination Class XII Results 2024')
            else:
                result_link = driver.find_element('partial link text','Senior School Certificate Examination (Class XII) Results 2024')

            while True:
                try:
                    result_link.click()
                    break
                except TimeoutException:
                    pass

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id,'txtRollno') or contains(@id,'regno') or contains(@placeholder,'oll')]")))


            try:
                driver.find_element(By.XPATH, "//input[contains(@id,'txtRollno') or contains(@id,'regno') or contains(@placeholder,'oll')]").send_keys('your_roll_no')
            except NoSuchElementException:
                driver.find_element(By.XPATH, "//*[contains(text(), 'Roll')]/../following-sibling::div/*").send_keys('your_roll_no')
            try:
                driver.find_element(By.XPATH, "//input[contains(@id,'schoolNo') or contains(@id,'sch') or contains(@placeholder,'chool')]").send_keys('your_school_no')
            except NoSuchElementException:
                driver.find_element(By.XPATH, "//*[contains(text(), 'School')]/../following-sibling::div/*").send_keys('your_school_no')
            try:
                driver.find_element(By.XPATH, "//input[contains(@id,'admitCardId') or contains(@id,'admid') or contains(@placeholder,'dmit')]").send_keys('your_admit_card_id')
            except NoSuchElementException:
                driver.find_element(By.XPATH, "//*[contains(text(), 'Admit')]/../following-sibling::div/*").send_keys('your_admit_card_id')

# since class X also requires DOB, you need to find the DOB element and insert your DOB
            # Use OCR to read captcha image
            try:
                captcha_element = driver.find_element(By.XPATH, "//img[contains(@id,'capimage') or contains(@id,'captcha') or contains(@id,'cap')]")
                captcha_element.screenshot('captcha.png')
                captcha_text = image_to_string(Image.open('captcha.png').resize((300,90)),config='--psm 13')
                if 'RX20' in captcha_text:
                    captcha_text = 'RX2OMO'
                captcha_text = captcha_text.lstrip("'")
                driver.find_element(By.XPATH, "//input[contains(@id,'txtcaptcha') or contains(@id,'captcha') or contains(@id,'cap') or contains(@id,'sec') or contains(@placeholder,'ecurity')]").send_keys(captcha_text)
            except NoSuchElementException:
                pass
            
            try:
                driver.find_element(By.XPATH, "//*[contains(@id,'Submit') or contains(@id,'submit') or contains(@value,'Submit') or contains(@value,'submit')]").click()
            except NoSuchElementException:
                driver.find_element(By.XPATH, "//*[contains(@id,'txtRollno') or contains(@id,'regno') or contains(@placeholder,'Roll')]").sendKeys(Keys.ENTER)
            except TimeoutException:
                continue

            WebDriverWait(driver, 10).until(text_present_in_page_source('ccountancy')) # replace 'ccountancy' with name of subject you have with first letter missing (like Hindi should be indi)
            screenshot_path = 'result_screenshot.png'
            driver.save_screenshot(screenshot_path)

            send_email(screenshot_path)
            break
    except TimeoutException:
        continue
    sleep(60)  # Check every 60 seconds

driver.quit()
