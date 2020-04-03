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


    def get_request(self, platformUrl):
        self.res = requests.get(platformUrl)
        #  print(res.raise_for_status) #[200] ok

    def get_buttons(self, buttonName, Id):
        
        #If webpage has buttons to navigate, it finds each one and moves between numbers
        time.sleep(10)
        try:
            #self.button = self.driver.find_elements_by_tag_name("button") #find button
            time.sleep(10)
            self.button = self.driver.find_element_by_xpath(buttonName)
            time.sleep(10)
            self.button.click()
        except:
            self.button = ''

        if Id == 'x':
            time.sleep(10)
            self.button = self.driver.find_elements_by_tag_name("button") #find button


    def get_elem(self, className):
        #Find class and retrieve data
        if className:
            try:
                #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, className)))   #waits until elements to be clickable are loaded
                time.sleep(10)
                self.elem = self.driver.find_elements_by_class_name(className)
                #print(self.elem)
            except:
                pass
        else:
            self.html = self.driver.page_source
            self.elem = bs4.BeautifulSoup(self.html)
        

    def get_items(self, className):
        #for each class founded in elem find all tags "a" which contains url link
        time.sleep(10)
        if className:
            for i in self.elem:
                self.items = [item for item in i.find_elements_by_tag_name("a")] #find a tag which contains href link
                #print(len(self.items)) #Check document with number of projects'''
        
        else:
            self.items = [item for item in self.elem.find_all('a')] #find a tag which contains href link
        
    
    def insert_Platform_Projects_database(self, Id, annexed, check, className, country):
        
        for item in self.items:

            try:
                if className:
                    Url = item.get_attribute('href')    #find href tag and url value
                    title = item.text
                
                else:
                    title = item.text.strip()
                    Url = str(item['href'])
            except:
                pass
            
            #Some href return route without main webage, in order to get the whole url I have to add main url
            if annexed : 
                Url = annexed + Url     


            try:

                if title : #Check if the tag has information
                    if check == '': #check the variable which contains the data to be checked (to clean urls)
                        if self.collection.find({ "Url": Url }).count() == 0: #check if url is already in database
                                        
                            try:
                                self.collection.insert_one({'Id': Id, 'Url':Url, 'Name': title, 'Country':country}) #insert in mongodb database
                            except Exception as e:
                                print(e)
                    elif str(check) in str(Url):    #check if values is in url
                        if self.collection.find({ "Url": Url }).count() == 0:    #check if url is already in database
                                        
                            try:
                                self.collection.insert_one({'Id': Id, 'Url':Url, 'Name': title, 'Country':country})
                            except Exception as e:
                                print(e)
            except:
                pass

    def get_Cs_Platform_Projects(self, Id, platformUrl, annexed, check, className, buttonName, country):     
        
        #Call def get_driver
        self.get_driver(platformUrl)
       
        if buttonName:       
            self.button = buttonName
    
            while self.button:
                    
                #Call def get_elem_by_class: retrieve class html code
                self.get_elem(className)

                #Call def get_elem:retrieve "a" tag
                self.get_items(className)
   
                #Call def insert_database: insert data retrieve into database
                self.insert_Platform_Projects_database(Id, annexed, check, className, country)                
            
                self.get_buttons(buttonName, Id)
                #self.button.click()
                time.sleep(10)

        else:
            
            if Id == 'x':

                self.get_buttons(buttonName, Id)

                for i in self.button: #iterate for ech button 
                    
                    if i.text.isdigit():
                        i.click() #select each button clicking on each one

                        #Call def get_elem_by_class: retrieve class html code
                        self.get_elem(className)

                        #Call def get_elem:retrieve "a" tag
                        self.get_items(className)
        
                        #Call def insert_database: insert data retrieve into database
                        self.insert_Platform_Projects_database(Id, annexed, check, className, country)   

            else :  
                #Call def get_elem_by_class: retrieve class html code
                self.get_elem(className)

                #Call def get_elem:retrieve "a" tag
                self.get_items(className)

                #Call def insert_database: insert data retrieve into database
                self.insert_Platform_Projects_database(Id, annexed, check, className, country)      


        time.sleep(5)
        self.driver.close()
    

    def get_Cs_Platform(self, Id, Name, platformUrl, annexed, check, className, buttonName, country):

        if self.collection_pla.find({ "Url": platformUrl }).count() == 0:
            self.collection_pla.insert_one({'Id': Id, 'Name':Name, 'Url':platformUrl, 'annexed': annexed, 'check': check, 'className': className, 'buttonName': buttonName, 'Country':country})

    def retrieve_platforms (self):
        for x in self.collection_pla.find():
            Id = list(x.values())[1]
            platformUrl = list(x.values())[3]
            annexed = list(x.values())[4]
            check = list(x.values())[5]
            className = list(x.values())[6]
            buttonName = list(x.values())[7]
            country = list(x.values())[8]
            
            self.get_Cs_Platform_Projects(Id, platformUrl, annexed, check, className, buttonName, country)

''' THIS PART WILL BE DONE WITN NER METHOD PROBABLY

    #Get for all the projects the information in tags  
    def getInfoProjects(self, projectUrl):
        res = requests.get(projectUrl)
        #  print(res.raise_for_status) #[200] 
        soup =bs4.BeautifulSoup(res.text,'html.parser')

        #For each tag 'div' recover tittle and description information
        for tag in soup.find_all('div'):            
                    
            for i in range(len(tag)):   #For each value in the tag
                
                titulo = tag.find_next('h1')    #Tittle tag
                try:    # If Attribute error then do nothing
                    if titulo.text.strip() and titulo.text.strip() not in projects[0:] :    #if tittle is informed and is not in project list
                        projects.append('TITULO')   #Add tittle and description for projects list
                        projects.append(titulo.text.strip())
                except AttributeError:
                    print('pff') 
                
                descriptivo = tag.find_all('p')      #Description information is in 'p' tag

                
                try:           
                    etiqueta = descriptivo[i].find_previous('h3')  #tittle information is in tag 'h3'
                    
                    if descriptivo[i].text.strip('\t') not in projects[0:] and etiqueta != None:    #if description is not in list and tittle is not empty
                        projects.append(etiqueta.text.strip())
                        projects.append(descriptivo[i].text.strip('\n'))
                        
                    elif descriptivo[i].text.strip('\t') not in projects[0:] :  #if description is not in list
                        projects.append('DATO')
                        projects.append(descriptivo[i].text.strip('\t'))
                        
                except IndexError:
                    print('pff')  

    #Convert a list as a dictionary
    def dictionaryConversion(lst): 

        for i in range(0, len(lst),2):  #For each value in list moving 2 steps for each loop


            if lst[i] not in list(res_dct.keys())  :    #If tittle is not in dictionary (key values)
                res_dct[lst[i]] = lst[i+1]      #Assign description to a tittle: one value each time
            else :                                      #If tittle is in dictionary 
                res_dct[lst[i]] = [str(res_dct[lst[i]]).strip('[]'),str(lst[i+1])]  #Create a list of values (strip separate values from previous list defined)

        return res_dct '''


#Populate the database with url platforms 
scraper = Scraper()
#(self, Id, Name, platformUrl, annexed, check, className, buttonName, country)
#scraper.get_Cs_Platform(184, 'Idereen Wetenschapper', 'https://www.iedereenwetenschapper.be/', 'https://www.iedereenwetenschapper.be', 'projects','overview-table','','BEL')
#Automatically retrieve projects from platforms listed in datase
#scraper.retrieve_platforms ()


#Populate the database with url projects for each platform
#(self, platformUrl, annexed, check, className, buttonName, country)
scraper.get_Cs_Platform_Projects(65, 'https://scistarter.org/finder', '', '','flex-grid','//*[@id="search-results"]/div[2]/div/button[2]','USA')







#Loop to read for each project in platform the tags informed
'''for x in collection.find():
    projects = []
    res_dct = {}
    #print(list(x.values())[1])
    getInfoProjects(list(x.values())[1])    #Retrieve all tag informed
    collection_proj.insert_one(dictionaryConversion(projects))  #For the dictionary created from a list, insert each one in database'''

