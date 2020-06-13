import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from zappa.asynchronous import task
from flask import Flask
app = Flask(__name__)


def login_to_starlink(driver: webdriver.Chrome, security_questions_and_answers: dict, username: str, password: str) -> None:
    """
    Given a chrome webdriver, login successfully to the subaru starlink portal and answer the challenge question
    :param username:
    :param password:
    :param security_questions_and_answers:
    :param driver:
    """
    print("Going to MySubaru..")
    driver.get('https://www.mysubaru.com/login.html')

    # ------------------------------------------------------------------------------------------------------

    # Find the username field
    print("Logging in..")
    username_box = driver.find_element_by_xpath('//form[@id="loginForm"]//input[@id="username"]')
    username_box.send_keys(username)

    # ------------------------------------------------------------------------------------------------------

    # Find the password field
    password_box = driver.find_element_by_xpath('//form[@id="loginForm"]//input[@id="password"]')
    password_box.send_keys(password)
    password_box.submit()

    # ------------------------------------------------------------------------------------------------------

    # Answer the security question
    security_answer_box_xpath = '//*[@id="securityQuestionModal"]//*[@class="form-group"]/input[@type="text"]'

    # Create a wait for the security pop up
    print("Waiting for security question..")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, 'securityQuestionText')))

    print("Answering security question..")
    security_question = driver.find_element_by_class_name('securityQuestionText')
    security_question_text = security_question.text

    if security_question_text not in security_questions_and_answers:
        sys.exit("Cannot find security question in given question/answers!")

    security_answer_box = driver.find_element_by_xpath(security_answer_box_xpath)
    security_answer_box.send_keys(security_questions_and_answers[security_question_text])

    security_submit = driver.find_element_by_xpath(
        '//*[@id="securityQuestionModal"]//button[@data-trn-key="common.submit"]')
    security_submit.click()


@task
def starlink_action(action: str) -> bool:
    """
    Given a driver and a action [lock, unlock], go ahead and login to starlink and perform the action
    Returning back a string with the actions return message
    :param action:
    :return:
    """

    # ------------------------------------------------------------------------------------------------------

    # environment variable for subaru starlink PIN
    PIN = os.environ.get('PIN')

    # environment variable for subaru starlink security question and answers
    security_questions_and_answers = {}
    for qa in os.environ.get('SECURITY_Q&A').split(','):
        question, answer = qa.split(':')
        security_questions_and_answers[question] = answer

    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')

    # ------------------------------------------------------------------------------------------------------

    options = Options()
    options.binary_location = 'lambda/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    # Optional argument, if not specified will search path.
    driver = webdriver.Chrome('lambda/chromedriver', options=options)

    print(f"Processing {action} action..")
    if action not in ['lock', 'unlock']:
        sys.exit("Unsupported action provided!")

    # ------------------------------------------------------------------------------------------------------

    # Process the initial login steps
    login_to_starlink(driver, security_questions_and_answers, username, password)

    # ------------------------------------------------------------------------------------------------------

    print("Waiting on action buttons..")
    starlink_action_button_xpath = f'//div[@id="starlinkActions"]//div[@id="{action}Button"]'
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, starlink_action_button_xpath)))

    # Find the lock/unlock button
    print("Pressing action button..")
    starlink_button = driver.find_element_by_xpath(starlink_action_button_xpath)
    starlink_button.click()

    pin_box = driver.find_element_by_xpath('//form[@id="starlinkOptionsForm"]//input[@id="pin"]')
    pin_box.send_keys(f'{PIN}\n')

    # ------------------------------------------------------------------------------------------------------

    # Return back the status message from Subaru
    status_message_xpath = '//div[@id="starlinkActions"]//div[@role="alert"]/*/span[@class="statusMessage"]'

    # Wait for status message
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, status_message_xpath)))

    status_message = driver.find_element_by_xpath(status_message_xpath)
    status_message_text = status_message.text

    print(f"Status: '{status_message_text}'")
    return True


def starlink_action_wrapper(action: str):
    """
    Wrap around the starlink action and provide error handing
    :param action:
    :return:
    """
    try:
        starlink_action(action)
    except:
        print("Unexpected error:", sys.exc_info()[0])

    return {
        "statusCode": 200,
        "body": "OK"
    }


@app.route('/lock')
def lock():
    return starlink_action_wrapper('lock')


@app.route('/unlock')
def unlock():
    return starlink_action_wrapper('unlock')


if __name__ == '__main__':
    app.run()
