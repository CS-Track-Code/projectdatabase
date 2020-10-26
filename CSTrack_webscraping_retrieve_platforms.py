import bs4, requests, pymongo, pprint, requests, time, re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import date
from langdetect import detect


from pymongo import MongoClient
from CSTrack_Mongo_conn import connection

class ScraperPlatforms:
    def __init__(self):
        #Mongodb connection
        self.conn = MongoClient(connection())


        #Mongodb database and repository
        db = self.conn.CSTrack

        #Collections
        self.collection_pla =  db.platforms_pla_list #Platforms
        self.collection = db.projects_pla_list   #Projects from platforms
        self.collection_proj = db.projects_pro_list  #Projects information
        self.CSTrack_config = db.CSTrack_config  #Projects information
        self.CSTrack_projects_descriptors = db.CSTrack_projects_descriptors  #Projects information

        self.CSTrack_platforms_projects = db.CSTrack_platforms_projects
        self.log_error = db.CSTrack_logerror #Store error for datacleaning


    def get_driver(self, platform_url, Id):
        #Selenium library read: Chromedriver route
        route = 'D:/Users/Miriam/Anaconda3/Lib/site-packages/selenium/webdriver/common/chromedriver.exe'
        
        #Open chrome
        self.driver = webdriver.Chrome(executable_path= route)
        
        #Get driver Url platform
        self.driver.get(platform_url)

        time.sleep(5)

        if str(platform_url) != str(self.driver.current_url):
            new_Url = str(self.driver.current_url)+"?tab=about"
            print(new_Url)
            #self.driver.close()
            #Get new driver Url platform
            self.driver.get(new_Url)


    def get_buttons(self, button_name, Id):
        
        #If webpage has buttons to navigate, it finds each one and moves between numbers
        time.sleep(10)

        try:
            #self.button = self.driver.find_elements_by_tag_name("button") #find button
            time.sleep(10)
            self.button = self.driver.find_element_by_xpath(button_name)
            time.sleep(10)
            self.button.click()
        except:
            self.button = ''

        if Id == 13:
            time.sleep(10)
            self.button = self.driver.find_elements_by_tag_name("button") #find button


    def get_elem(self, class_name):
        #Find class and retrieve data
        if class_name:
            try:
                #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, className)))   #waits until elements to be clickable are loaded
                time.sleep(15)
                self.elem = self.driver.find_elements_by_class_name(class_name)                #print(self.elem)
            except:
                pass
        else:
            self.html = self.driver.page_source
            self.elem = bs4.BeautifulSoup(self.html)

      
    def get_items(self, class_name, tag):
        #for each class founded in elem find all tags "a" which contains url link
        time.sleep(15)
        if class_name:
            for i in self.elem:
                self.items = [item for item in i.find_elements_by_tag_name(tag)] #find a tag which contains href link
                #print(len(self.items)) #Check document with number of projects'''
        
        else:
            self.items = [item for item in self.elem.find_all(tag)] #find a tag which contains href link
        

    def insert_Platform_Projects_database(self, Id, annexed, check, class_name, country):
        
        for item in self.items:

            try:
                if class_name:
                    Url = item.get_attribute('href')    #find href tag and url value
                    title = item.text
                        
                else:
                    title = item.text.strip()
                    Url = str(item['href'])
            except:
                pass
            
            #Some href return route without main webage, in order to get the whole url I have to add main url
            
            try:
                if annexed : 
                    Url = annexed + Url     
            except:
                pass

            #ID = 124 exception, modify url. Crawler gets diferent values for same platform
            

            try:

                if title : #Check if the tag has information
                    if check == '': #check the variable which contains the data to be checked (to clean urls)
                        if self.collection.find({ "Url": Url }).count() == 0: #check if url is already in database
                                            
                            try:
                                self.collection.insert_one({'Id': Id, 'Url':Url, 'Name': title, 'Country':country, 'load_date': str(date.today())}) #insert in mongodb database
                            except Exception as e:
                                print(e)

                    elif str(check) in str(Url):    #check if values is in url
                        if self.collection.find({ "Url": Url }).count() == 0:    #check if url is already in database
                                            
                            try:
                                self.collection.insert_one({'Id': Id, 'Url':Url, 'Name': title, 'Country':country, 'load_date': str(date.today())})
                            except Exception as e:
                                print(e)
            except:
                pass

    def extract_insert_projects_platforms(self, Id, annexed, check, class_name, country):  
        #Call def get_elem_by_class: retrieve class html code
        self.get_elem(class_name)

        #Call def get_elem:retrieve "a" tag
        self.get_items(class_name, "a")
        
        #Call def insert_database: insert data retrieve into database
        self.insert_Platform_Projects_database(Id, annexed, check, class_name, country)                
                   
        time.sleep(15)


    def get_Cs_Platform_Projects(self, Id, platform_url, annexed, check, class_name, button_name, country):     
        
        #last button
        last = 0

        #Call def get_driver
        self.get_driver(platform_url, Id)
       
        if button_name:       
            self.button = button_name
    
            while self.button:
                        
                self.extract_insert_projects_platforms( Id, annexed, check, class_name, country)              
                
                self.get_buttons(button_name, Id)
                time.sleep(15)             

        else:
            
            if Id == 13 and self.execution_type == 'manually':

                self.get_buttons(button_name, Id)

                for i in self.button: #iterate for ech button 
                    
                    if i.text.isdigit():
                        
                        #Check if is the last sheet
                        if last < int(i.text):
                            last = int(i.text)
                            i.click() #select each button clicking on each one

                            self.extract_insert_projects_platforms( Id, annexed, check, class_name, country)

                        else:
                            break
            
            elif Id == 17 and self.execution_type == 'manually':
                               
                for i in range(1,12):

                    self.driver.close()

                    #List of elements
                    Url = "https://eu-citizen.science/projects?page=" + str(i)
                    print(Url)

                    #Call def get_driver
                    self.get_driver(Url, Id)

                    #Extract elements
                    self.extract_insert_projects_platforms( Id, annexed, check, class_name, country)

            elif Id == 37 and self.execution_type == 'manually':

                count =  self.driver.find_elements_by_class_name("ecosystempager")
                
                for i in range(2,len(count)):

                    self.driver.close()
                    
                    #List of elements
                    Url = "https://www.open-sciences-participatives.org/ecosysteme-sciences-participatives/?p=" + str(i)

                    #Call def get_driver
                    self.get_driver(Url, Id)

                    #Extract elements
                    self.extract_insert_projects_platforms( Id, annexed, check, class_name, country)
            
            elif Id == 38 and self.execution_type == 'manually':

                for i in range(1,8):

                    self.driver.close()
                    
                    #List of elements
                    Url = "https://ldf.lv/en/list_of_projects#qt-projects_archive-ui-tabs" + str(i)

                    #Call def get_driver
                    self.get_driver(Url, Id)
                    
                    #Extract elements
                    self.extract_insert_projects_platforms( Id, annexed, check, class_name, country)

            else :  
                #Extract elements
                self.extract_insert_projects_platforms( Id, annexed, check, class_name, country)

        self.driver.close()
    
    def retrieve_platforms (self, Id, execution_type):

        self.execution_type = execution_type

        if Id :
            for x in self.collection_pla.find({"Id": Id}):
                
                Id = list(x.values())[1]
                platform_url = list(x.values())[3]
                annexed = list(x.values())[4]
                check = list(x.values())[5]
                class_name = list(x.values())[6]

                if execution_type == 'manually':
                    button_name = list(x.values())[7]
                else:
                    button_name = ''

                country = list(x.values())[8]

                #if is informed as to be loaded
                if list(x.values())[10] == 'yes' and list(x.values())[11] == 'Automatic':
                    self.get_Cs_Platform_Projects(Id, platform_url, annexed, check, class_name, button_name, country)

        else:
            for x in self.collection_pla.find() :
                Id = list(x.values())[1]
                platform_url = list(x.values())[3]
                annexed = list(x.values())[4]
                check = list(x.values())[5]
                class_name = list(x.values())[6]

                if execution_type == 'manually':
                    button_name = list(x.values())[7]
                else:
                    button_name = ''

                country = list(x.values())[8]

                #if is informed as to be loaded
                if list(x.values())[10] == 'yes' and list(x.values())[11] == 'Automatic' :
                    self.get_Cs_Platform_Projects(Id, platform_url, annexed, check, class_name, button_name, country)
                else:
                    continue    #if not, continue

