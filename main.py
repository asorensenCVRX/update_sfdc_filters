from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import os
import time
import pandas as pd
from pprint import pprint


# # run database.py
# with open("database.py") as f:
#     code = f.read()
#     exec(code)


def create_csv(excel_path, csv_path1, csv_path2):
    df = pd.read_excel(excel_path, sheet_name=0)
    filtered_df1 = df[df['LNAME_REP'].str.startswith(tuple(map(chr, range(ord('A'), ord('M')))))]
    filtered_df1.to_csv(csv_path1, index=False)
    filtered_df2 = df[df['LNAME_REP'].str.startswith(tuple(map(chr, range(ord('M'), ord('Z') + 1))))]
    filtered_df2.to_csv(csv_path2, index=False)


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

username = os.environ['USERNAME']
password = os.environ['PASSWORD']

dashboard_urls = {
    'Daily Driver': 'https://cvrx.lightning.force.com/lightning/r/Dashboard/01Z4u000000WX7lEAG/view',
    'Regional': 'https://cvrx.lightning.force.com/lightning/r/Dashboard/01Z4u000000WX9IEAW/view?queryScope=userFolders',
    'Regional AM Detail': 'https://cvrx.lightning.force.com/lightning/r/Dashboard/01Z4u000001OCgqEAG/view?queryScope'
                          '=userFolders',
    'Commercial Business Activity': 'https://cvrx.lightning.force.com/lightning/r/Dashboard/01Z4u000001ai1AEAQ/view',

}


def delete_current_list_items():
    current_filter_values = driver.find_element(By.CLASS_NAME, 'filter-option-list').find_elements(By.TAG_NAME,
                                                                                                   'li')
    for item in current_filter_values:
        try:
            delete = item.find_element(By.CSS_SELECTOR, 'button[title*=Remove]')
            delete.click()
        except StaleElementReferenceException:
            delete_current_list_items()
        except NoSuchElementException:
            break


def add_new_list_items(file_path):
    data = pd.read_csv(file_path)
    names = data['NAME'].tolist()
    for name in names:
        driver.find_element(By.ID, 'addFilterValueBtn').click()
        input_value_field = driver.find_element(By.ID, 'undefined-input')
        input_value_field.send_keys(name)
        driver.find_element(By.CLASS_NAME, 'filter-apply').click()
    driver.find_element(By.ID, 'submitBtn').click()


def update_picklist(num, filepath):
    """num needs to equal 1 or 2: 1 if you are editing A-L and 2 if you are editing M-Z. Filepath is for the csv file
    with the names you are uploading."""
    num += 1
    owner_dropdown_container = driver.find_element(By.CLASS_NAME, f'widget-container_{num}')
    pencil_button = owner_dropdown_container.find_element(By.CSS_SELECTOR, 'button.editFilter')
    pencil_button.send_keys(Keys.ENTER)
    time.sleep(2)
    pencil_button.send_keys(Keys.ENTER)
    time.sleep(1)
    delete_current_list_items()
    try:
        add_new_list_items(filepath)
    except NoSuchElementException:
        driver.find_element(By.CSS_SELECTOR, 'button[title=Close]').click()
        update_picklist(num - 1, filepath)


def log_in():
    print("Logging in...")
    log_in_button = driver.find_element(By.XPATH, '//*[@id="idp_section_buttons"]/button')
    log_in_button.click()
    time.sleep(5)
    username_field = driver.find_element(By.ID, 'i0116')
    username_field.send_keys(username)
    driver.find_element(By.ID, 'idSIButton9').click()
    # time.sleep(2)
    # password_field = driver.find_element(By.ID, 'i0118')
    # password_field.send_keys(password)
    # driver.find_element(By.ID, 'idSIButton9').click()
    time.sleep(40)


def run_selenium():
    loop = 1
    for key, value in dashboard_urls.items():
        print(f"Opening {key} Dashboard...")
        driver.get(value)
        if key == 'Daily Driver':
            log_in()
        if loop > 1:
            time.sleep(40)

        # switch iframe
        iframe = driver.find_element(By.CSS_SELECTOR, "iframe[title='dashboard']")
        driver.switch_to.frame(iframe)

        # edit
        driver.find_element(By.CSS_SELECTOR, 'button.edit').click()
        time.sleep(2)

        # update picklist 1
        print("Updating last names A through L...")
        update_picklist(1, "./A through L.csv")

        # update picklist 2
        print("Updating last names M through Z...")
        update_picklist(2, "./M through Z.csv")
        save = driver.find_element(By.CSS_SELECTOR, 'button.save')
        save.click()
        loop += 1
        time.sleep(10)


# RUN SCRIPT HERE
# create_csv("./names.xlsx", "./A through L.csv", "./M through Z.csv")
run_selenium()
