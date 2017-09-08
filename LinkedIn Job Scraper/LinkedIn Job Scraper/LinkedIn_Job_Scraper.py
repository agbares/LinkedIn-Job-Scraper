from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import getpass
import time
import csv

loginURL = "https://www.linkedin.com/uas/login"
searchURL = "https://www.linkedin.com/jobs/search/?f_E=1&f_TP=1%2C2%2C3%2C4&keywords=software&location=United%20States&locationId=us%3A0"

driver = webdriver.Firefox()
wait = WebDriverWait(driver, 12)

fieldNames = ['Company Name', 'Job Title', 'Location', 'Date Posted', 'Easy Apply?', 'URL']
filename = "output.csv"

email = ""
passsword = ""

#   CreateCSV()
#
#   This function creates a new CSV file under path and writes
#       the fieldNames to the first row
#
#   Params: 
#       path -- Location/filename for the CSV output
#
def createCSV(path, fieldNames):
    with open(path, "w", newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter = ',')
        writer.writerow(fieldNames)

#   writeToCSV()
#
#   This function writes the created dictionary to the CSV file under path. 
#
#   Params:
#       path -- Location/filename for the CSV output
#       fieldNames -- Field Names/Header for the CSV columns
#       dictionary -- Row data to be written to the CSV
#
def writeToCSV(path, fieldNames, dictionary):
    with open(path, "a", newline='') as outFile:
        writer = csv.DictWriter(outFile, fieldNames, delimiter = ',', dialect = 'excel')

        for entry in dictionary:
            writer.writerow(entry)

#   createDictionary()
#
#   This function creates a dictionary for each row of entries to be inserted
#       to the CSV file
#
#   Params:
#       entries -- Job listing entry data
#       fieldNames -- Field Names/Header for the CSV columns
#
#   Return: dictionary
#
def createDictionary(entries, fieldNames):
    dictionary = []
    for entry in entries:
        innerDictionary = dict(zip(fieldNames, entry))
        dictionary.append(innerDictionary)

    return dictionary

#   scrollToBottom()
#
#   Utility function that gradually scrolls down to the page, taking into account
#       that the search page loads listings when in view
#
def scrollToBottom():
    pageHeight = driver.execute_script("return document.body.scrollHeight")

    for i in range(1, 100):
        driver.execute_script("window.scrollBy(0, " + str((pageHeight / 100) * i)  + ")", "")

#   getUserDetails()
#
#   Requests user for email and password on the terminal
#
def getUserDetails():
    global email
    global password

    email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")

#   login()
#
#   Logs in the user with the given credentials then opens the
#       search page
#
#   Return: Boolean
#
def login():
    # Log into LinkedIn
    driver.get(loginURL)

    element = driver.find_element_by_id("session_key-login")
    element.send_keys(email)

    element = driver.find_element_by_id("session_password-login")
    element.send_keys(password)

    element.submit()

    # If the navigation bar loads, then the user must be logged in
    try:
        wait.until(EC.visibility_of_element_located((By.ID, "extended-nav")))
    
    except TimeoutException:
        driver.quit()
        return False

    # Search Page
    driver.get(searchURL)

    try:
        wait.until(EC.visibility_of_element_located((By.ID, "sort-dropdown-select")))

    except TimeoutException:
        driver.quit()
        return False

#   scrapeData()
#
#   Searches through the page for all job listings and calls relevant functions
#       to export listings data to CSV
#
#   Params: 
#       path -- Location/filename for the CSV output
#       fieldNames -- Field Names/Header for the CSV columns
#
#   Return: Boolean
#
def scrapeData(path, fieldNames):
    scrollToBottom()

    elements = driver.find_elements_by_class_name("job-card__link-wrapper")
    companyNames = driver.find_elements_by_class_name("job-card__company-name")
    datesPosted = driver.find_elements_by_class_name("job-card__listed-status")
    locations = driver.find_elements_by_class_name("job-card__location")
    jobCards = driver.find_elements_by_class_name("job-card--column")

    entries = list()

    index = 0

    for element in elements:
        if element.text != "":

            hasElement = True
            isEasyApply = ""

            # TODO: Figure out how to determine if posting allows Easy Apply

            #try:
            #    element.find_element_by_xpath("//*[text() = 'Easy Apply']")

            #except NoSuchElementException: 
            #    hasElement = False

            #if hasElement:
            #    isEasyApply = "Yes"

            #else:
            #    isEasyApply = "No"

            jobTitle = element.text
            URL = element.get_attribute('href')
            ID = jobCards[index].get_attribute('id')
            companyName = companyNames[index].text
            datePosted = datesPosted[index].text
            location = locations[index].text
            location = location[location.find("\n") + 1 : len(location)]

            plainURL = URL[0 : URL.find('?')]

            entries.append([companyName, jobTitle, location, datePosted, isEasyApply, plainURL])
            
            index += 1

    dictionary = createDictionary(entries, fieldNames)
    writeToCSV(path, fieldNames, dictionary)

    # If the current page is the last page, then there shouldn't be a next button and we can exit the program
    try:
        driver.find_element_by_class_name("next").click()

    except NoSuchElementException:
        driver.quit()
        return False

    return True

def main():
    createCSV(filename, fieldNames)

    if getUserDetails() == False:
        raise SystemExit

    if login() == False:
        raise SystemExit

    firstPass = True
    while firstPass or scrapeData(filename, fieldNames):
        firstPass = False

if __name__ == '__main__':
    main()
