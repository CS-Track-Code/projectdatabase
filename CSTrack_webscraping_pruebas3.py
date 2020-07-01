import bs4, requests, pymongo, pprint, requests, time, re

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
        #conn = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false') #localhost
        conn = MongoClient('mongodb://root:g9k.LS00-1!JbzA8..@internal-docker.sb.upf.edu:8327/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')
        #conn = MongoClient('mongodb://root:g9k.LS00-1!JbzA8..@internal-docker.sb.upf.edu:8336/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')


        #Mongodb database and repository
        db = conn.CSTrack

        #Collections
        self.collection_pla =  db.platforms_pla_list #Platforms
        self.collection = db.projects_pla_list   #Projects from platforms
        self.collection_proj = db.projects_pro_list  #Projects information
        self.CSTrack_config = db.CSTrack_config  #Projects information

        self.CSTrack_platforms_projects = db.CSTrack_platforms_projects


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

        if Id == 13:
            time.sleep(10)
            self.button = self.driver.find_elements_by_tag_name("button") #find button


    def get_elem(self, className):
        #Find class and retrieve data
        if className:
            try:
                #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, className)))   #waits until elements to be clickable are loaded
                time.sleep(15)
                self.elem = self.driver.find_elements_by_class_name(className)                #print(self.elem)
            except:
                pass
        else:
            self.html = self.driver.page_source
            self.elem = bs4.BeautifulSoup(self.html)

      
    def get_items(self, className, tag):
        #for each class founded in elem find all tags "a" which contains url link
        time.sleep(15)
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
            
            try:
                if annexed : 
                    Url = annexed + Url     
            except:
                pass

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

    def get_Cs_Platform_Projects(self, Id, platformUrl, annexed, check, className, buttonName, country):     
        
        #last button
        last = 0

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
                time.sleep(15)             

        else:
            
            if Id == 13:

                self.get_buttons(buttonName, Id)

                for i in self.button: #iterate for ech button 
                    
                    if i.text.isdigit():
                        
                        #Check if is the last sheet
                        if last < int(i.text):
                            last = int(i.text)
                            i.click() #select each button clicking on each one

                            #Call def get_elem_by_class: retrieve class html code
                            self.get_elem(className)

                            #Call def get_elem:retrieve "a" tag
                            self.get_items(className, "a")
            
                            #Call def insert_database: insert data retrieve into database
                            self.insert_Platform_Projects_database(Id, annexed, check, className, country)   
                        else:
                            break
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
        print(platformUrl)
        if self.collection_pla.find({ "Url": platformUrl }).count() == 0:
            self.collection_pla.insert_one({'Id': Id, 'Name':Name, 'Url':platformUrl, 'annexed': annexed, 'check': check, \
                'className': className, 'buttonName': buttonName, 'Country':country, 'ProjClassName': '', 'Load': 'yes'})

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

                #if is informed as to be loaded
                if list(x.values())[10] == 'yes':
                    self.get_Cs_Platform_Projects(Id, platformUrl, annexed, check, className, buttonName, country)

        else:
            for x in self.collection_pla.find():
                Id = list(x.values())[1]
                platformUrl = list(x.values())[3]
                annexed = list(x.values())[4]
                check = list(x.values())[5]
                className = list(x.values())[6]
                buttonName = list(x.values())[7]
                country = list(x.values())[8]

                #if is informed as to be loaded
                if list(x.values())[10] == 'yes':
                    self.get_Cs_Platform_Projects(Id, platformUrl, annexed, check, className, buttonName, country)
                else:
                    continue    #if not, continue

    def descriptors_definition (self):

        #Retrieve descriptors - DEFINITIONS
        self.web = ['WEB'] #Add web to the list
        self.mail = ['MAIL'] #Add mail to the list 
        self.description = ['DESCRIPTION'] #Add description to the list
        self.social_media = ['SOCIAL MEDIA']  #Add media to the list
        self.app = ['APPS'] #Add apps to the list
        self.images = ['IMAGES'] #Add images to the list
        self.resources = ['RESOURCES'] #Add resources to the list
        self.geo = ['GEOGRAPHICAL LOCATION'] #Add geography location to the list
        self.status = ['STATUS'] #Add status to the list
        self.methodology = ['METHODOLOGY']  #Add metodology to the list
        self.start_date = ['START DATE']  #Add start date to the list
        self.investment = ['INVESTMENT']  #Add investment to the list
        self.topic = ['TOPICS'] #Add topics to the list
        self.time = ['DEVELOPMENT TIME']  #Add development time to the list
        self.objectives = ['MAIN OBJECTIVES']  #Add objectives to the list
        self.ages = ['MEMBER AGE']  #Add ages to the list
        self.space = ['DEVELOPMENT SPACE'] #Add space to the list
        self.duration = ['DEDICATION TIME']  #Add duration to the list
        self.update_date = ['PLATFORM UPDATE DATE'] #Add update_date to the list
        self.dedication = ['DEDICATION TIME']  #Add dedication to the list
        self.main = ['MAIN PROGRAM OR PERSON IN CHARGE']  #Add main program to the list
        self.participants = ['PARTICIPANTS PROFILE'] #Add profile to the list
        self.tools = ['TOOLS AND MATERIALS'] #Add tools & materials to the list


        #check if social media values are in this list
        self.social_media_values = self.CSTrack_config.find({ "Id": 6 })[0]
        #check if files values are in this list
        self.files_values = self.CSTrack_config.find({ "Id": 8 })[0]
        #check if apps values are in this list
        self.apps_values = self.CSTrack_config.find({ "Id": 10 })[0]
        #check if imgaes values are in this list
        self.images_values = self.CSTrack_config.find({ "Id": 35 })[0]    
        #check if Geographical values are in this list
        self.geo_values = self.CSTrack_config.find({ "Id": 15 })[0]  
        #check if Status values are in this list
        self.status_values = self.CSTrack_config.find({ "Id": 20 })[0] 
        #check if Methodology values are in this list
        self.methodology_values = self.CSTrack_config.find({ "Id": 18 })[0] 
        #check if Start date values are in this list
        self.start_date_values = self.CSTrack_config.find({ "Id": 21 })[0] 
        #check if Investment date values are in this list
        self.investment_values = self.CSTrack_config.find({ "Id": 31 })[0] 
        #check if Topic values are in this list
        self.topic_values = self.CSTrack_config.find({ "Id": 12 })[0] 
        #check if Development time values are in this list
        self.time_values = self.CSTrack_config.find({ "Id": 23 })[0] 
        #check if Main objectives values are in this list
        self.objectives_values = self.CSTrack_config.find({ "Id": 4 })[0] 
        #check if ages values are in this list
        self.ages_values = self.CSTrack_config.find({ "Id": 26 })[0] 
        #check if developement space values are in this list
        self.space_values = self.CSTrack_config.find({ "Id": 36 })[0] 
        #check if dedication time values are in this list
        self.dedication_values = self.CSTrack_config.find({ "Id": 37 })[0] 
        #check if main programe or person in charge values are in this list
        self.main_value = self.CSTrack_config.find({ "Id": 27 })[0] 
        #check if update date values are in this list
        self.update_date_values = self.CSTrack_config.find({ "Id": 39 })[0] 
        #check if participants profile values are in this list
        self.participants_profile_values = self.CSTrack_config.find({ "Id": 29 })[0] 
        #check if tools values are in this list
        self.tools_values = self.CSTrack_config.find({ "Id": 19 })[0] 



    def projects_descriptors(self, Id, projectUrl, Name, Plat_country, className):

        self.get_elem(className)

        # Tag "a" - mail / web / img / social media
        self.get_items(className, "a")

        try:
            for item in self.items: 
                if item.get_attribute('href'):
                    self.checkDescriptors(item.get_attribute('href'))
        except:
            pass 
          

        if int(Id) == 193:
            #¡¡¡¡REVISAR ESTO PORQUE NO HAY MANERA!!!!
            # Tag "div" - description + others

            self.get_items(className, "h1")
            print(self.items)

            for item in self.items:
                
                print(item.text.strip())
    

            self.get_items(className, "h2")
            print(self.items)

            for item in self.items:

                print(item.text.strip())


                #inerhtml =item.get_attribute('innerHTML')
                #print(inerhtml)
                #outerhtml =item.get_attribute('outerHTML')
                #tag_value=outerhtml.split('',1)[0] # to extract first word
                #print(outerhtml)

                #text = item.text.split('\n')

            '''self.get_items(className, "div")
            
            for item in self.items:
                text = item.text.split('\n')
                print(text)
                
            self.get_items(className, "span")'''
            
            for item in self.items:
                text2 = item.text.split('\n')
                
  
        elif int(Id) == 17:
            #¡¡¡¡REVISAR ESTO PORQUE NO HAY MANERA!!!!
            # Tag "p" - description + others
            self.get_items(className, "class")

        
        else:
            
            # Tag "p" - description + others
            self.get_items(className, "p")
            
            try:

                #Specific behaviour for Id:184
                if str(Id) == '184':
                    
                    item = self.items[0]
                    self.checkDescriptors(item.text)

                    for i in range(1,len(self.items),2):
                        item = self.items[i]
                        desc = self.items[i+1]
                        #Concatenar título y texto
                        self.checkDescriptors(item.text+" : "+desc.text)
                
                else:                      
                    for item in self.items:
                        self.checkDescriptors(item.text)
                
            except:
                pass
            

            # Tag "table" - description + others
            self.get_items(className, "tr")

            try:
                for item in self.items:
                    self.checkDescriptors(item.text.replace('\n', ' ') )
            except:
                pass


            # Tag "span" - description + others
            self.get_items(className, "span")

            try:
                for item in self.items:

                    self.checkDescriptors(item.text)
            except:
                pass


        # Tag "h1" & "h2" & "h6" - title

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

        try:
            self.get_items(className, "h6")
            if self.items and Id == 147: #If not empty
                if item.text and item.text not in self.main[0:] :    #if tittle is informed and is not in project list                        
                    self.main.append(item.text)
        except:
            pass

        #some projects inform TITLE with "Estadísticas del evento"
        if int(Id) == 111:
            if "Estadísticas del evento" in self.title[1] :
                self.title.pop()
                self.title.append(Name)



        #After complete all the lists, Platform Id, Platform country and current date is updated
        self.Id_plat = ["Plat Id", Id]
        self.country_plat = ["Plat country", Plat_country]
        self.insert_date = ["Insert date", date.today()]
        self.Url_platform = ["Url platform", projectUrl]

    #Check text extracted conditions
    def checkDescriptors(self, value):

        if '@' in str(value):
            #print(item.get_attribute('href'))
            if value and value not in self.mail[0:] :    #if tittle is informed and is not in project list
                self.mail.append(value)
                self.description.append(value)

        elif ('www.' in str(value) or 'http' in str(value)) and ' ' not in str(value):
            #print(value)
            if value:    #if tittle is informed and is not in project list                        
                #social media check
                if any(ele in value for ele in self.social_media_values['values']):
                    if value  not in self.social_media[0:]: 
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
                #If is a link to ages profile
                elif any(ele in value for ele in self.ages_values['values']) :
                    if value not in self.ages[0:]:    
                        self.ages.append(value)
                #If is a link to topics profile
                elif any(ele in value for ele in self.topic_values['values']) :
                    if value not in self.topic[0:]:    
                        self.topic.append(value)
                elif any(ele in value for ele in self.main_value['values']) :
                    if value not in self.main[0:]:    
                        self.main.append(value)
                elif any(ele in value for ele in self.participants_profile_values['values']) :
                    if value not in self.participants[0:]:    
                        self.participants.append(value)
                elif any(ele in value for ele in self.geo_values['values']) :
                    if value not in self.geo[0:]:    
                        self.geo.append(value)
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
            elif any(ele in value for ele in self.objectives_values['values']) :
                if value not in self.objectives[0:]:    
                    self.objectives.append(value)
            elif any(ele in value for ele in self.time_values['values']) :
                if value not in self.time[0:]:    
                    self.time.append(value)
            elif any(ele in value for ele in self.ages_values['values']) :
                if value not in self.ages[0:]:    
                    self.ages.append(value)
            elif any(ele in value for ele in self.space_values['values']) :
                if value not in self.space[0:]:    
                    self.space.append(value)
            elif any(ele in value for ele in self.dedication_values['values']) :
                if value not in self.dedication[0:]:    
                    self.dedication.append(value)
            elif any(ele in value for ele in self.ages_values['values']) :
                    if value not in self.ages[0:]:    
                        self.ages.append(value)
            elif any(ele in value for ele in self.update_date_values['values']) :
                if value not in self.update_date[0:]:    
                    self.update_date.append(value)
            elif any(ele in value for ele in self.participants_profile_values['values']):
                if value not in self.participants[0:]:    
                    self.participants.append(value)
            elif any(ele in value for ele in self.main_value['values']):
                if value not in self.main[0:]:    
                    self.main.append(value)
            elif any(ele in value for ele in self.tools_values['values']):
                if value not in self.tools[0:]:    
                    self.tools.append(value)
            else:
                self.description.append(value)


    #Convert a list as a dictionary
    def dictionaryConversion(self): 

        #Create a list of lists to read automatically the data retrieved
        self.dictionary = [tuple(self.title),tuple(self.web), tuple(self.social_media), tuple(self.mail), 
        tuple(self.description), tuple(self.Id_plat), tuple(self.country_plat), tuple(self.insert_date), 
        tuple(self.app), tuple(self.images), tuple(self.resources), tuple(self.geo), tuple(self.status), tuple(self.methodology), 
        tuple(self.start_date), tuple(self.investment), tuple(self.topic), tuple(self.time), tuple(self.ages), tuple(self.dedication) ,
        tuple(self.space), tuple(self.update_date), tuple(self.Url_platform), tuple(self.main), tuple(self.participants), tuple(self.objectives),
        tuple(self.tools)]


        print(self.dictionary)

        self.desc_dict = {}
        self.lista = self.dictionary[0]

        #Check if is in dictionary
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
                    if i != 0 and i != 5 and i != 6 and i != 7 and i != 22:
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
    
        #PLATFORM ORIGIN Url        
            print(self.Url_platform)
            value = self.Url_platform

            if self.collection_proj.find({ "$and" : [ { "TITLE": str(self.lista[1])}, { "Url platform": value } ]}).count() == 0:
                self.collection_proj.update( { "TITLE": str(self.lista[1])},  { "$set": { "Url platform": value} })

    def retrieve_projects (self, Id):

        project =self.collection_pla.find({"Id": Id})[0]
        
        #CHECK IF WORK
        if str(self.collection_pla.find({"Id":Id})[0].get("Load")) == 'yes':
            for x in self.CSTrack_platforms_projects.find({"Id": Id}):
                Id = list(x.values())[1]
                Url = list(x.values())[2]
                Name = list(x.values())[3]
                country = list(x.values())[4]

                #If it does not exist, then continue. if it exists then do nothing and check the next one
                if self.collection_proj.find({ "Url platform": Url }).count() == 0: 
                    #Initialize lists
                    self.descriptors_definition ()
                    
                    #Get driver: Add ?tab=about for '111' link
                    
                    if str(Id) == '111':
                        LastUrl = str(Url)+"?tab=about"
                        #Call def get_driver
                        self.get_driver(LastUrl)
                    else:
                        #Call def get_driver
                        self.get_driver(Url)

                    #Get ClassName and iterate
                    Class = project.get("ProjClassName")
                    
                    #Get elements and all the information for each descriptor
                    if Class:
                        #Check if a list and iterate, if not, then pass Class element
                        if isinstance(Class, str) :
                            self.projects_descriptors(Id, Url, Name, country, Class)
                        
                        else:
                            for i in list(Class):
                                self.projects_descriptors(Id, Url, Name, country, i)

                    else:
                        self.projects_descriptors(Id, Url, Name, country, '')

                    #Close
                    time.sleep(5)
                    self.driver.close()


                    #Call for dictionary conversion and insert or update into database
                    self.dictionaryConversion()



    def pruebas(self, Id, projectUrl, Name, Plat_country, className):

        
        #Initialize lists
        self.descriptors_definition ()

        self.projects_descriptors(Id, projectUrl, Name, Plat_country, className)

        #Close
        time.sleep(5)
        self.driver.close()

        #Call for dictionary conversion and insert or update into database
        self.dictionaryConversion()


           
#Populate the database with url platforms #apper
scraper = Scraper()

#Pendiente de decidir como leer span y div
#scraper.projects_descriptors('193','https://biocollect.ala.org.au/acsa/project/index/f300d3ac-3024-48a3-a8b6-229d075ff276', 'DK', 'AUT', 'pill-content')

#scraper.pruebas('111','https://www.inaturalist.org/projects/intersex-ducks', 'iNaturalista', 'iNaturalista','', 'stracked')


#scraper.get_Cs_Platform(34, 'Jagis pour la nature', 'http://www.vigienature.fr/fr', 'http://www.vigienature.fr', '/fr/','', '','FR')
#scraper.get_Cs_Platform_Projects(193, 'https://biocollect.ala.org.au/acsa#isCitizenScience%3Dtrue%26isWorldWide%3Dfalse%26max%3D20%26sort%3DdateCreatedSort', '', '/project/','', '//a[@href="javascript:pago.nextPage();"]','AUS')
scraper.retrieve_projects(65)
#scraper.retrieve_platforms (184)
#scraper.pruebas(111, 'https://www.inaturalist.org/projects/milkweed-madness-monarch-waystation', '"Milkweed Madness" Monarch Waystation', 'World', '')


#Loop to read for each project in platform the tags informed
'''for x in collection.find():
    projects = []
    res_dct = {}
    #print(list(x.values())[1])
    getInfoProjects(list(x.values())[1])    #Retrieve all tag informed
    collection_proj.insert_one(dictionaryConversion(projects))  #For the dictionary created from a list, insert each one in database'''

