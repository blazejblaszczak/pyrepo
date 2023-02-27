from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time

# webdriver creation when using imported chrome driver
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# webdriver creation when using local chrome driver
chrome_driver_path = 'C:\\Workspace\\Development\\chromedriver.exe'
driver = webdriver.Chrome(executable_path=chrome_driver_path)

website = 'https://www.python.org/'
driver.get(website)

# Creating dictionary with upcoming events

dates = [driver.find_element(By.XPATH, f'//*[@id="content"]/div/section/div[2]/div[2]/div/ul/li[{i}]/time').text
            for i in range(1, 6)]
events = [driver.find_element(By.XPATH, f'//*[@id="content"]/div/section/div[2]/div[2]/div/ul/li[{i}]/a').text
            for i in range(1, 6)]

events_dict = {}

for i in range(len(dates)):
    events_dict[i] = {'time': dates[i], 'name': events[i]}

print(events_dict)

# clicking link based on link text

learn_more = driver.find_element(By.LINK_TEXT, "Learn More")
learn_more.click()

# making input in search box

search = driver.find_element(By.ID, "id-search-field")
search.send_keys('Python')
search.send_keys(Keys.ENTER)

time.sleep(2.5)

# driver.close() # closes tab
driver.quit() # closes whole browser
