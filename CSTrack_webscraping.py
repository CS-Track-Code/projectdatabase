import bs4, requests, pymongo, pprint, requests, time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import date


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
        self.CSTrack_config = db.CSTrack_config  #Projects information


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
                self.elem = self.driver.find_elements_by_class_name(className)                #print(self.elem)
            except:
                pass
        else:
            self.html = self.driver.page_source
            self.elem = bs4.BeautifulSoup(self.html)

      
    def get_items(self, className, tag):
        #for each class founded in elem find all tags "a" which contains url link
        time.sleep(10)
        if className:
            for i in self.elem:
                self.items = [item for item in i.find_elements_by_tag_name(tag)] #find a tag which contains href link
                #print(len(self.items)) #Check document with number of projects'''
        
        else:
            self.items = [item for item in self.elem.find_all(tag)] #find a tag which contains href link
        

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
                self.get_items(className, "a")
   
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
                        self.get_items(className, "a")
        
                        #Call def insert_database: insert data retrieve into database
                        self.insert_Platform_Projects_database(Id, annexed, check, className, country)   

            else :  
                #Call def get_elem_by_class: retrieve class html code
                self.get_elem(className)

                #Call def get_elem:retrieve "a" tag
                self.get_items(className, "a")

                #Call def insert_database: insert data retrieve into database
                self.insert_Platform_Projects_database(Id, annexed, check, className, country)


        time.sleep(5)
        self.driver.close()
    

    def get_Cs_Platform(self, Id, Name, platformUrl, annexed, check, className, buttonName, country):

        if self.collection_pla.find({ "Url": platformUrl }).count() == 0:
            self.collection_pla.insert_one({'Id': Id, 'Name':Name, 'Url':platformUrl, 'annexed': annexed, 'check': check, 'className': className, 'buttonName': buttonName, 'Country':country})

    def retrieve_platforms (self, Id):

        if Id :
            for x in self.collection_pla.find({"Id": Id}):
                Id = list(x.values())[1]
                platformUrl = list(x.values())[3]
                annexed = list(x.values())[4]
                check = list(x.values())[5]
                className = list(x.values())[6]
                buttonName = list(x.values())[7]
                country = list(x.values())[8]
                
                self.get_Cs_Platform_Projects(Id, platformUrl, annexed, check, className, buttonName, country)
        else:
            for x in self.collection_pla.find({"Id": Id}):
                Id = list(x.values())[1]
                platformUrl = list(x.values())[3]
                annexed = list(x.values())[4]
                check = list(x.values())[5]
                className = list(x.values())[6]
                buttonName = list(x.values())[7]
                country = list(x.values())[8]
                
                self.get_Cs_Platform_Projects(Id, platformUrl, annexed, check, className, buttonName, country)


    def projects_descriptors(self, Id, projectUrl, Name, Plat_country, className):
        
                #Retrieve descriptors - DEFINITIONS
        self.web = []
        self.web.append('WEB') #Add web for web list
        self.mail = []
        self.mail.append('MAIL')   #Add mail for mail list 
        self.description = []
        self.description.append('DESCRIPTION')   #Add description for mail list
        self.social_media = []
        self.social_media.append('SOCIAL MEDIA')   #Add media for mail list
        self.app = []
        self.app.append('APPS')   #Add apps for mail list
        self.images = []
        self.images.append('IMAGES')   #Add images for mail list
        self.resources = []
        self.resources.append('RESOURCES')   #Add images for mail list
        self.geo = []
        self.geo.append('GEOGRAPHICAL LOCATION')   #Add images for mail list
        self.status = []
        self.status.append('STATUS')   #Add images for mail list
        self.methodology = []
        self.methodology.append('METHODOLOGY')   #Add images for mail list
        self.start_date = []
        self.start_date.append('START DATE')   #Add images for mail list
        self.investment = []
        self.investment.append('INVESTMENT')   #Add images for mail list
        self.topic = []
        self.topic.append('TOPICS')   #Add images for mail list
        self.time = []
        self.time.append('DEVELOPMENT TIME')   #Add images for mail list
        
        #check if social media values are in this list
        self.social_media_values = self.CSTrack_config.find({ "Id": 1 })[0]
        #check if files values are in this list
        self.files_values = self.CSTrack_config.find({ "Id": 2 })[0]
        #check if apps values are in this list
        self.apps_values = self.CSTrack_config.find({ "Id": 3 })[0]
        #check if imgaes values are in this list
        self.images_values = self.CSTrack_config.find({ "Id": 4 })[0]    
        #check if Geographical values are in this list
        self.geo_values = self.CSTrack_config.find({ "Id": 5 })[0]  
        #check if Status values are in this list
        self.status_values = self.CSTrack_config.find({ "Id": 6 })[0] 
        #check if Methodology values are in this list
        self.methodology_values = self.CSTrack_config.find({ "Id": 7 })[0] 
        #check if Start date values are in this list
        self.start_date_values = self.CSTrack_config.find({ "Id": 8 })[0] 
        #check if Investment date values are in this list
        self.investment_values = self.CSTrack_config.find({ "Id": 9 })[0] 
        #check if Topic values are in this list
        self.topic_values = self.CSTrack_config.find({ "Id": 10 })[0] 
        #check if Development time values are in this list
        self.time_values = self.CSTrack_config.find({ "Id": 11 })[0] 
        
        #Call def get_driver
        self.get_driver(projectUrl)
        
        self.get_elem(className)

        # Tag "a" - mail / web / img / social media
        self.get_items(className, "a")
        
        try:
            for item in self.items: 
                self.checkDescriptors(item.get_attribute('href'))
        except:
            pass

        # Tag "p" - description + others
        self.get_items(className, "p")

        try:
            for item in self.items:
                self.checkDescriptors(item.text)
        except:
            pass

        # Tag "h1" - title

        self.title = []
        self.title.append('TITLE')   #Add tittle 

        try:        
            
            self.get_items(className, "h1")
            if self.items: #If not empty
                for item in self.items:
                    if item.text and item.text not in self.title[0:] :    #if tittle is informed and is not in project list                        
                        self.title.append(item.text)
            else: #If empty h1 then check h2
                self.get_items(className, "h2")
                if self.items:  #If not empty
                    for item in self.items:
                        if item.text and item.text not in self.title[0:] :    #if tittle is informed and is not in project list                        
                            self.title.append(item.text)
                else:   #If empty get Project Name from platform extraction
                    self.title.append(Name)
        except:
            self.title.append(Name)

        #After complete all the lists, Platform Id, Platform country and current date is updated
        self.Id_plat = ["Plat Id", Id]
        self.country_plat = ["Plat country", Plat_country]
        self.insert_date = ["Insert date", date.today()]

        #Call for dictionary conversion and insert or update into database
        self.dictionaryConversion()

        time.sleep(5)
        self.driver.close()

    #Check text extracted conditions
    def checkDescriptors(self, value):

        if '@' in str(value):
            #print(item.get_attribute('href'))
            if value and value not in self.mail[0:] :    #if tittle is informed and is not in project list
                self.mail.append(value)

        elif 'www.' in str(value) or 'http' in str(value):
            #print(item.text)
            if value:    #if tittle is informed and is not in project list                        
                #social media check
                if any(ele in value for ele in self.social_media_values['values']):
                    if value  not in self.social_media[0:]: #Añadir posibles webs a excluir, redes sociales ppial. list [].
                        self.social_media.append(value)    
                #If is a resource
                elif any(ele in value for ele in self.files_values['values']) :
                    if value  not in self.resources[0:]:    
                        self.resources.append(value) 
                #If is an app
                elif any(ele in value for ele in self.apps_values['values'])  :
                    if value not in self.app[0:]:    
                        self.app.append(value) 
                #If is an image
                elif any(ele in value for ele in self.images_values['values']) :
                    if value not in self.images[0:]:    
                        self.images.append(value)
                elif value not in self.web[0:] :       
                    self.web.append(value)

        elif value not in self.description[0:]:
            #Some URL has no 'www' or 'http' text      
            if any(ele in value for ele in self.apps_values['values']) :
                if value not in self.app[0:]:    
                    self.app.append(value) 
            elif any(ele in value for ele in self.geo_values['values']) :
                if value not in self.geo[0:]:    
                    self.geo.append(value)
            elif any(ele in value for ele in self.status_values['values']) :
                if value not in self.status[0:]:    
                    self.status.append(value)
            elif any(ele in value for ele in self.methodology_values['values']) :
                if value not in self.methodology[0:]:    
                    self.methodology.append(value)
            elif any(ele in value for ele in self.start_date_values['values']) :
                if value not in self.start_date[0:]:    
                    self.start_date.append(value)
            elif any(ele in value for ele in self.investment_values['values']) :
                if value not in self.investment[0:]:    
                    self.investment.append(value)
            elif any(ele in value for ele in self.topic_values['values']) :
                if value not in self.topic[0:]:    
                    self.topic.append(value)
            elif any(ele in value for ele in self.time_values['values']) :
                if value not in self.time[0:]:    
                    self.time.append(value)
            else:
                self.description.append(value)


    #Convert a list as a dictionary
    def dictionaryConversion(self): 

        #Create a list of lists to read automatically the data retrieved
        self.dictionary = [tuple(self.title),tuple(self.web), tuple(self.social_media), tuple(self.mail), 
        tuple(self.description), tuple(self.Id_plat), tuple(self.country_plat), tuple(self.insert_date), 
        tuple(self.app), tuple(self.images), tuple(self.resources), tuple(self.geo), tuple(self.status), tuple(self.methodology), 
        tuple(self.start_date), tuple(self.investment), tuple(self.topic), tuple(self.time) ]
                
        self.desc_dict = {}
        self.lista = self.dictionary[0]

        #Check if is in database
        '''print(self.lista)
        print(self.title)
        print(self.collection_proj.find({ "TITLE": self.lista[1] }))'''

        if self.collection_proj.find({ "TITLE": self.lista[1] }).count() != 0: #IS IN DICTIONARY
                
            self.update_descriptors()
        
        #If not, create dictionary
        else:   
            #REVISAR EL APPEND DE LA WEBS SI HAY MAS DE UNO
            for i in range(0, len(self.dictionary)):  #For each value in list moving 2 steps for each loop
                
                #Get all the lists defined in dictionary
                self.lista = self.dictionary[i]
                
                try:
                    #If length is > 2 then there is a title and a list of values
                    if i != 0 and i != 5 and i != 6 and i != 7:
                        if len(self.lista[1:len(self.lista)])>0:   #if not empty
                            self.desc_dict[self.lista[0]] = self.lista[1:len(self.lista)]
                    else:
                        #If length is = 2 then there is a title and only one value
                        if len(str(self.lista[1]))>0:  #if not empty
                            self.desc_dict[self.lista[0]] = str(self.lista[1])
                except:
                    pass
            
            #Insert new
            self.insert_descriptors()

    def insert_descriptors(self):
        #The dictionary is not in the database, insert all new
        self.collection_proj.insert_one(self.desc_dict)
        
    def update_descriptors(self):
        #The dictionary is in databse (checked the title), then, update values
        platform_id = self.collection_proj.find({ "TITLE": str(self.lista[1]) })[0]
       
        #Check if the descriptors are in database for each one
        #WEB
        for i in range(1,len(self.web)):
            
            value = self.web[i]
            
            if self.collection_proj.find({ "$and" : [ { "TITLE": str(self.lista[1])}, { "WEB": value } ]}).count() == 0:
                self.collection_proj.update( { "TITLE": str(self.lista[1])},  { "$push": { "WEB": value} })

        #MAIL
        for i in range(1,len(self.mail)):

            value = self.mail[i]
 
            if self.collection_proj.find({ "$and" : [ { "TITLE": str(self.lista[1])}, { "MAIL": value } ]}).count() == 0:
                self.collection_proj.update( { "TITLE": str(self.lista[1])},  { "$push": { "MAIL": value} })

        #DESCRIPTION        
        for i in range(1,len(self.description)):

            value = self.description[i]

            if self.collection_proj.find({ "$and" : [ { "TITLE": str(self.lista[1])}, { "DESCRIPTION": value } ]}).count() == 0:
                self.collection_proj.update( { "TITLE": str(self.lista[1])},  { "$push": { "DESCRIPTION": value} })

        #SOCIAL MEDIA        
        for i in range(1,len(self.social_media)):

            value = self.social_media[i]

            if self.collection_proj.find({ "$and" : [ { "TITLE": str(self.lista[1])}, { "SOCIAL MEDIA": value } ]}).count() == 0:
                self.collection_proj.update( { "TITLE": str(self.lista[1])},  { "$push": { "SOCIAL MEDIA": value} })

    def retrieve_projects (self, Id):

        project =self.collection_pla.find({"Id": Id})[0]
        

        for x in self.collection.find({"Id": Id}):
            Id = list(x.values())[1]
            Url = list(x.values())[2]
            Name = list(x.values())[3]
            country = list(x.values())[4]
            
            self.projects_descriptors(Id, Url, Name, country, project.get("ProjClassName"))
            
           
#Populate the database with url platforms 
scraper = Scraper()
#scraper.projects_descriptors('https://biocollect.ala.org.au/acsa/project/index/de5317df-eeb4-412d-bbea-56d79889f9a2', 'container-fluid')
#scraper.get_Cs_Platform(211, 'Science Cite', 'https://www.science-et-cite.ch/de/home/projekte/projekte-national-und-deutschschweiz?limit=20&tag_list_language_filter=de-DE&types[0]=1&start=0', 'https://www.science-et-cite.ch/', '/de/','', '//*[@id="content"]/div[3]/ul/li[6]/a','SWZ')

scraper.retrieve_projects(174)
#scraper.retrieve_platforms (174)

#Loop to read for each project in platform the tags informed
'''for x in collection.find():
    projects = []
    res_dct = {}
    #print(list(x.values())[1])
    getInfoProjects(list(x.values())[1])    #Retrieve all tag informed
    collection_proj.insert_one(dictionaryConversion(projects))  #For the dictionary created from a list, insert each one in database'''

