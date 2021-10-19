import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


import os.path

import csv

from dotenv import load_dotenv
load_dotenv()



# data structure: title (commit message), pass/fail, branch name, date executed, time taken

class NavigateSite:

    def __init__(self, url):
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.get(url)
        self.outputFile = "workflows_tests.csv"

    def Login(self, uname, pwd):
        try:

            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@id='login_field']")))

            unameLog = self.driver.find_element_by_xpath("//input[@id='login_field']")
            passLog = self.driver.find_element_by_xpath("//input[@id='password']")

            unameLog.send_keys(uname)
            passLog.send_keys(pwd)

            loginBtn = self.driver.find_element_by_xpath( "//input[@class='btn btn-primary btn-block js-sign-in-button']")
            loginBtn.click()


            self.NavigateToActions();

        except TimeoutException:
            print("Loading is taking too long")

    def NavigateToActions(self):
        try:
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//a[@id='actions-tab']")))
            actionBtn = self.driver.find_element_by_xpath( "//a[@id='actions-tab']")
            actionBtn.click()

            # get page number
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='paginate-container']")))

            pagination_parent = self.driver.find_element_by_xpath("/html[1]/body[1]/div[4]/div[1]/main[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[7]/div[1]/div[1]")
            child_anchors = pagination_parent.find_elements_by_xpath('.//a')
            page_count = int(child_anchors[-2].text)+1

            #fields to be acquired
            data = [['Commit Message', 'Date Executed', 'Duration', 'Branch Name', 'Test Comment', 'Pass']]

            for _ in range(1, int(page_count)):
                # get row items count 
                row_count = len(self.driver.find_elements_by_class_name('Box-row'));
                
                for x in range(1,int(row_count) + 1):

                    xPathTitle = "/html[1]/body[1]/div[4]/div[1]/main[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[6]/div[2]/div["
                    xPathTitle += str(x)
                    xPathTitle += "]/div[1]/div[1]/span[1]/a[1]"

                    xPathIsPass = "/html[1]/body[1]/div[4]/div[1]/main[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[6]/div[2]/div["
                    xPathIsPass += str(x)
                    xPathIsPass += "]/div[1]/div[1]/div[1]/div[1]"

                    xPathBranchName = "/html[1]/body[1]/div[4]/div[1]/main[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[6]/div[2]/div["
                    xPathBranchName += str(x)
                    xPathBranchName += "]/div[1]/div[2]/a[1]"

                    xPathDateExe = "/html[1]/body[1]/div[4]/div[1]/main[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[6]/div[2]/div["
                    xPathDateExe += str(x)
                    xPathDateExe += "]/div[1]/div[3]/div[1]/div[1]/span[1]/time-ago[1]"     

                    xPathDuration = "/html[1]/body[1]/div[4]/div[1]/main[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[6]/div[2]/div["
                    xPathDuration += str(x)
                    xPathDuration += "]/div[1]/div[3]/div[1]/div[1]/details[1]/summary[1]/span[1]"

                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xPathTitle)))
                    
                    title = self.driver.find_element_by_xpath(xPathTitle).text

                    isPass_element = self.driver.find_element_by_xpath(xPathIsPass)
                    testComment = isPass_element.get_attribute("title")

                    branch = self.driver.find_element_by_xpath(xPathBranchName).text

                    date_exe_element = self.driver.find_element_by_xpath(xPathDateExe)
                    date_exe = date_exe_element.get_attribute("title")

                    duration = self.driver.find_element_by_xpath(xPathDuration).text

                    if(testComment == "This workflow run completed successfully."):
                        isPass = True
                    else:
                        isPass = False

                    row_data = [title, date_exe, duration, branch, testComment,isPass]

                    data.append(row_data)


                getNext = self.driver.find_element_by_class_name('next_page')
                getNext.click()

            self.OutputCSV(data)

        except TimeoutException:
            print("Loading is taking too long")

    def OutputCSV(self, data):

        with open(self.outputFile, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        
        self.driver.quit()
        
web = NavigateSite(os.getenv("URL_LINK"))

web.Login(os.getenv("USER_NAME") , os.getenv("PWD"))