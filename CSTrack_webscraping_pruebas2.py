import bs4, requests, pymongo, pprint, requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

from pymongo import MongoClient

class Scraper:
    def __init__(self):
        #Mongodb connection
        conn = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')

        #Mongodb database and repository
        db = conn.CSTrack

        #Collections
        self.collection_pla =  db.platforms_pla_list #Platforms
        self.collection = db.projects_pla_list   #Projects from platforms
        self.collection_proj = db.projects_pro_list  #Projects information


    def get_driver(self, platformUrl):
        #Selenium library read: Chromedriver route
        route = 'D:/Users/Miriam/Anaconda3/Lib/site-packages/selenium/webdriver/common/chromedriver.exe'
        
        #Open chrome
        self.driver = webdriver.Chrome(executable_path= route)
        
        #Get driver Url platform
        self.driver.get(platformUrl)

        self.html = self.driver.page_source
        
    def get_request(self, platformUrl):
        self.res = requests.get(platformUrl)
        #  print(res.raise_for_status) #[200] ok

    def get_buttons(self):
        
        #If webpage has buttons to navigate, it finds each one and moves between numbers
        time.sleep(10)
        button = self.driver.find_elements_by_tag_name("button") #find button
        return button

    def get_elem(self, className):
        #Find class and retrieve data
        if className:
            try:
                #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, className)))   #waits until elements to be clickable are loaded
                time.sleep(5)
                self.elem = self.driver.find_elements_by_class_name(className)
                print(self.elem)
            except:
                pass
        else:
            self.elem = bs4.BeautifulSoup(self.html)
        

    def get_items(self, className):
        #for each class founded in elem find all tags "a" which contains url link
        time.sleep(5)
        if className:
            for i in self.elem:
                self.items = [item for item in i.find_elements_by_tag_name("a")] #find a tag which contains href link
                print(len(self.items)) #Check document with number of projects'''
        
        else:
            self.items = [item for item in self.elem.find_all('a')] #find a tag which contains href link
        
    
    def insert_database(self, annexed, check, className, country):
        
        for item in self.items:
            print(item)
            if className:
                Url = item.get_attribute('href')    #find href tag and url value
                print(Url)
                title = item.text
                print(title)
            else:
                title = item.text.strip()
                Url = str(item['href'])
            
            #Some href return route without main webage, in order to get the whole url I have to add main url
            if annexed : 
                Url = annexed + Url     

            try:

                if item.text : #Check if the tag has information
                    if check == '': #check the variable which contains the data to be checked (to clean urls)
                        if self.collection.find({ "Url": Url }).count() == 0: #check if url is already in database
                                        
                            try:
                                self.collection.insert_one({'Url':Url, 'Name': title, 'Country':country}) #insert in mongodb database
                            except Exception as e:
                                print(e)
                    elif str(check) in str(Url):    #check if values is in url
                        if self.collection.find({ "Url": Url }).count() == 0:    #check if url is already in database
                                        
                            try:
                                self.collection.insert_one({'Url':Url, 'Name': title, 'Country':country})
                            except Exception as e:
                                print(e)
            except:
                pass

    def getCsPlatformProjects(self, platformUrl, annexed, check, className, buttonName, country): 
        
        
        #Call def get_driver
        self.get_driver(platformUrl)


        #Call def get_elem_by_class: retrieve class html code
        self.get_elem(className)

        
        #Call def get_elem:retrieve "a" tag
        self.get_items(className)

        #Call def insert_database: insert data retrieve into database
        self.insert_database(annexed, check, className, country)
                   
        
        time.sleep(5)
        self.driver.close()
    

scraper = Scraper()
scraper.getCsPlatformProjects('https://biocollect.ala.org.au/acsa#isCitizenScience%3Dtrue%26isWorldWide%3Dfalse%26max%3D500%26sort%3DdateCreatedSort','','project',"row-fluid", '','')

#('https://ecsa.citizen-science.net/community/list', '','profile-organization_profile','','','USA')
#('https://www.zooniverse.org/projects', '', 'projects', "project-card-list", '', '')


#('https://www.zooniverse.org/projects', '', 'projects', "project-card-list", '', '')
                            
#('https://scistarter.org/finder','','','flex-grid','','')
#('https://www.zooniverse.org/projects', '', 'projects', "project-card-list", '', '')
#('https://biocollect.ala.org.au/acsa#isCitizenScience%3Dtrue%26isWorldWide%3Dfalse%26max%3D500%26sort%3DdateCreatedSort','','project',"row-fluid", '//*[@id="pt-navLinks"]/div','')


#('https://www.zooniverse.org/projects', '', 'projects', "project-card-list", '')
#('https://biocollect.ala.org.au/acsa#isCitizenScience%3Dtrue%26isWorldWide%3Dfalse%26max%3D500%26sort%3DdateCreatedSort','','project',"row-fluid", '', '')

#('https://www.zooniverse.org/projects', '', 'projects', "project-card-list", '')


'''button = self.get_buttons
        print(button)
        
        #time.sleep(5)
        #button = self.driver.find_elements_by_tag_name("button") #find button
        
        time.sleep(10)
        button = self.driver.find_element_by_xpath('//*[@id="search-results"]/div[2]/div/button[2]/i')
    
        while button:
            #button = self.driver.find_element_by_xpath('//*[@id="search-results"]/div[2]/div/button[2]/i')
            button.click()
            time.sleep(10)

        
        for i in button: #iterate for ech button 
            print(i.text)
            if i.text.isdigit():
                i.click() #select each button clicking on each one
                #print(i.text)   '''