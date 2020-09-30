import bs4, requests, pymongo, pprint, requests, time, re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import date
from langdetect import detect


from pymongo import MongoClient

class Scraper:
    def __init__(self):
        #Mongodb connection
        #conn = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false') #localhost
        #self.conn = MongoClient('mongodb://root:g9k.LS00-1!JbzA8..@internal-docker.sb.upf.edu:8327/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')
        self.conn = MongoClient('mongodb://root:g9k.LS00-1!JbzA8..@internal-docker.sb.upf.edu:8336/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')


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


    def get_driver(self, platformUrl, Id):
        #Selenium library read: Chromedriver route
        route = 'D:/Users/Miriam/Anaconda3/Lib/site-packages/selenium/webdriver/common/chromedriver.exe'
        
        #Open chrome
        self.driver = webdriver.Chrome(executable_path= route)
        
        #Get driver Url platform
        self.driver.get(platformUrl)

        time.sleep(5)

        if str(platformUrl) != str(self.driver.current_url):
            New_Url = str(self.driver.current_url)+"?tab=about"
            print(New_Url)
            #self.driver.close()
            #Get new driver Url platform
            self.driver.get(New_Url)


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

    def extract_insert_projects_platforms(self, Id, annexed, check, className, country):  
        #Call def get_elem_by_class: retrieve class html code
        self.get_elem(className)

        #Call def get_elem:retrieve "a" tag
        self.get_items(className, "a")
        
        #Call def insert_database: insert data retrieve into database
        self.insert_Platform_Projects_database(Id, annexed, check, className, country)                
                   
        #self.button.click()
        time.sleep(15)


    def get_Cs_Platform_Projects(self, Id, platformUrl, annexed, check, className, buttonName, country):     
        
        #last button
        last = 0

        #Call def get_driver
        self.get_driver(platformUrl, Id)
       
        if buttonName:       
            self.button = buttonName
    
            while self.button:
                        
                self.extract_insert_projects_platforms( Id, annexed, check, className, country)              
                
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

                            self.extract_insert_projects_platforms( Id, annexed, check, className, country)

                        else:
                            break
            
            elif Id == 17:
                               
                for i in range(1,12):

                    self.driver.close()

                    #List of elements
                    Url = "https://eu-citizen.science/projects?page=" + str(i)
                    print(Url)

                    #Call def get_driver
                    self.get_driver(Url, Id)

                    #Extract elements
                    self.extract_insert_projects_platforms( Id, annexed, check, className, country)

            elif Id == 37 :

                count =  self.driver.find_elements_by_class_name("ecosystempager")
                
                for i in range(2,len(count)):

                    self.driver.close()
                    
                    #List of elements
                    Url = "https://www.open-sciences-participatives.org/ecosysteme-sciences-participatives/?p=" + str(i)

                    #Call def get_driver
                    self.get_driver(Url, Id)

                    #Extract elements
                    self.extract_insert_projects_platforms( Id, annexed, check, className, country)
            
            elif Id == 38:

                for i in range(1,8):

                    self.driver.close()
                    
                    #List of elements
                    Url = "https://ldf.lv/en/list_of_projects#qt-projects_archive-ui-tabs" + str(i)

                    #Call def get_driver
                    self.get_driver(Url, Id)
                    
                    #Extract elements
                    self.extract_insert_projects_platforms( Id, annexed, check, className, country)

            else :  
                #Extract elements
                self.extract_insert_projects_platforms( Id, annexed, check, className, country)

        self.driver.close()
    

    def get_Cs_Platform(self, Id, Name, platformUrl, annexed, check, className, buttonName, country, type, language, platform_load, projects_load):
        print(platformUrl)
        if self.collection_pla.find({ "Url": platformUrl }).count() == 0:
            self.collection_pla.insert_one({'Id': Id, 'Name':Name, 'Url':platformUrl, 'annexed': annexed, 'check': check, \
                'className': className, 'buttonName': buttonName, 'Country':country, 'ProjClassName': '', 'Load': 'yes',  \
                'Platform load': platform_load, 'Projects load': projects_load, 'Type': type, 'Wp2 Id':Id, 'Language': language })

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
                if list(x.values())[10] == 'yes' and list(x.values())[11] == 'Automatic':
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
        self.duration = ['DURATION']  #Add duration to the list
        self.update_date = ['PLATFORM UPDATE DATE'] #Add update_date to the list
        self.dedication = ['DEDICATION TIME']  #Add dedication to the list
        self.main = ['MAIN PROGRAM OR PERSON IN CHARGE']  #Add main program to the list
        self.participants = ['PARTICIPANTS PROFILE'] #Add profile to the list
        self.tools = ['TOOLS AND MATERIALS'] #Add tools & materials to the list
        self.num_members = ['NUMBER OF MEMBERS'] #Add number of members to the list
        self.end_date = ['END DATE'] #Add end date to the list
        self.results = ['RESULTS'] #Add results to the list

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
        #check if number of members values are in this list
        self.num_members_values = self.CSTrack_config.find({ "Id": 24 })[0] 
        #check if end date values are in this list
        self.end_date_values = self.CSTrack_config.find({ "Id": 22 })[0] 
        #check if web values are in this list
        self.web_values = self.CSTrack_config.find({ "Id": 5 })[0]

    def projects_descriptors(self, Id, projectUrl, Name, Plat_country, className):

        self.get_elem(className)

        # Tag "a" - mail / web / img / social media
        self.get_items(className, "a")

        try:
            for item in self.items: 
                if item.get_attribute('href'):

                    if str(Id) == '13':

                        if 'team' in projectUrl :
                                
                            if item not in self.participants[0:]:   
                                self.participants.append(item.get_attribute('href'))
                        else:
                            self.checkDescriptors(item.get_attribute('href'))
                    else:
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
            
            for item in self.items:
                text2 = item.text.split('\n')
                
  
        elif int(Id) == 17:
            #¡¡¡¡REVISAR ESTO PORQUE NO HAY MANERA!!!!
            # Tag "p" - description + others
            self.get_items(className, "class")

        elif int(Id) == 32:
            #¡¡¡¡REVISAR ESTO PORQUE NO HAY MANERA!!!!
            # Tag "p" - description + others
            self.get_items(className, "br")

            try:
                for item in self.items: 
                    self.checkDescriptors(item.text)
            except:
                pass 

            # Tag "p" - description + others
            self.get_items(className, "p")
            
            try: 
            
                for item in self.items:
                    self.checkDescriptors(item.text.replace('\n', ' '))

            except:
                pass

        elif int(Id) == 174:
            
            self.get_items(className, 'div')
            
            text_list = self.items[0].text.split('\n')
            description = ''

            for i in text_list:
                #For all the values in a list, find all the titles (upper case) and description (lower case)
                if i.isupper() :
                    if description :
                        text = text + ' ' + description
                        self.checkDescriptors(text)
                        description = ''
                        text = i
                    else:
                        text = i
                else:
                    if description:
                        description = description + ' , ' + i
                    else:
                        description = i
            
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
                        #Two tabs one for The team and other for resources shoud be stored in participants and results lists
                        if str(Id) == '13':

                            if 'team' in projectUrl :
                                
                                if item not in self.participants[0:]:   
                                    self.participants.append(item.text)

                            elif 'results' in projectUrl:
                                if item not in self.participants[0:]:    
                                     self.results.append(item.text)
                            
                            elif 'faq' in projectUrl:
                                if item not in self.methodology[0:]:    
                                     self.methodology.append(item.text)
                            
                            elif 'education' in projectUrl:
                                if item not in self.methodology[0:]:    
                                     self.resources.append(item.text)

                            else:
                               self.checkDescriptors(item.text.replace('\n', ' '))
                        else:
                            self.checkDescriptors(item.text.replace('\n', ' '))
                
            except:
                pass
            

            # Tag "table" - description + others
            self.get_items(className, "tr")

            try:
                for item in self.items: 
                    self.checkDescriptors(item.text.replace('\n', ' ') )
            except:
                pass

            # Tag "list" - description + others
            self.get_items(className, "li")

            try:
                for item in self.items: 

                    if str(Id) == '13':

                        if 'team' in projectUrl :
                                
                            if item not in self.participants[0:]:   
                                self.participants.append(item.text)
                        else:
                            self.checkDescriptors(item.text)
                    else:
                        self.checkDescriptors(item.text.replace('\n', ' ') )
                    
            except:
                pass


            # Tag "span" - description + others
            self.get_items(className, "span")

            try:
                for item in self.items:

                    if str(Id) == '13':

                            if 'team' in projectUrl :
                                #No store this information, we have it as a list
                                pass

                            else:
                               self.checkDescriptors(item.text)
                    else:
                        self.checkDescriptors(item.text)

            except:
                pass


        # Tag "h1" & "h2" & "h6" - title

        self.title = []
        self.title.append('TITLE')   #Add tittle 

        
        try:        
            #Special tittle for Id 35
            if Id == 35 :

                self.get_items("", "h1")
               
                if self.items: #If not empty
                    self.title.append(item.text)
                
            else:

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
                            
                            #h2 retrieve important information
                            if int(Id) == 63:
                                self.checkDescriptors(item.text.replace('\n', ' ') ) 

                    else:   #If empty get Project Name from platform extraction
                        self.title.append(Name)
                        
                        print(Name)
        except:
            self.title.append(Name)

        try:
            self.get_items(className, "h6")
            if self.items and Id == 147 : #If not empty
                if item.text and item.text not in self.main[0:] :    #if tittle is informed and is not in project list                        
                    self.main.append(item.text)
        except:
            pass

        #some projects inform TITLE with "Estadísticas del evento"
        if int(Id) == 111:
            if "Estadísticas del evento" in self.title[1] or 'Estadísticas' in self.title[1]:
                self.title.pop()
                self.title.append(Name)
        elif int(Id) == 60:
            if "Otros proyectos" in self.title[1] :
                self.title.pop()
                self.title.append(Name)
        elif int(Id) == 66:
            if "Contenido" in self.title[1] :
                self.title.pop()
                self.title.append(Name)
        
        if  int(Id) == 63 or int(Id) == 13:
            self.title = ['TITLE']
            self.title.append(Name)


        #After complete all the lists, Platform Id, Platform country and current date is updated
        self.Id_plat = ["Plat Id", Id]
        self.country_plat = ["Plat country", Plat_country]
        self.insert_date = ["Insert date", date.today()]
        self.Url_platform = ["Url platform", self.initialUrl]

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
            elif any(ele in value for ele in self.num_members_values['values']):
                if value not in self.num_members[0:]:    
                    self.num_members.append(value)
            elif any(ele in value for ele in self.end_date_values['values']):
                if value not in self.end_date[0:]:    
                    self.end_date.append(value)
            elif any(ele in value for ele in self.web_values['values']):
                if value not in self.web[0:]:    
                    self.web.append(value)
            else:
                self.description.append(value)


    #Convert a list as a dictionary
    def dictionaryConversion(self, Id, country, wp2_id, language): 

        #Create a list of lists to read automatically the data retrieved
        self.dictionary = [tuple(self.title),tuple(self.web), tuple(self.social_media), tuple(self.mail), 
        tuple(self.description), tuple(self.Id_plat), tuple(self.country_plat), tuple(self.insert_date), 
        tuple(self.app), tuple(self.images), tuple(self.resources), tuple(self.geo), tuple(self.status), tuple(self.methodology), 
        tuple(self.start_date), tuple(self.investment), tuple(self.topic), tuple(self.time), tuple(self.ages), tuple(self.dedication) ,
        tuple(self.space), tuple(self.update_date), tuple(self.Url_platform), tuple(self.main), tuple(self.participants), tuple(self.objectives),
        tuple(self.tools), tuple(self.num_members), tuple(self.end_date), tuple(self.results)]

        #Check if tittle is ¡Eso no existe!
        if self.title[1] == "¡Eso no existe!" or "Se ha interrumpido la conexión" in self.title[1]:
            self.check_errors()
        else:
            print(self.dictionary)

            self.desc_dict = {}
            self.lista = self.dictionary[0]

            # #Check if is in dictionary descriptors
            # if self.CSTrack_projects_descriptors.find({ "TITLE": self.lista[1] }).count() != 0: #IS IN DICTIONARY
                    
            #     self.update_descriptors(Id, country, wp2_id, language)
            
            #If not, create dictionary
            #else: 
              
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
                

    def insert_descriptors(self):
        #The dictionary is not in the database, insert all new
        #self.collection_proj.insert_one(self.desc_dict)
        try:
            self.collection_proj.insert_one(self.desc_dict)
        except pymongo.errors.AutoReconnect:
            db = self.conn.CSTrack
            db.projects_pro_list.insert_one(self.desc_dict)

    def check_errors(self):
        # Update log error to inform that the project does not exist 
        self.log_error.insert_one({"Error type": "Project does not exist", "Id": str(self.Id_plat[1]), "Error": "Check the URL: " + str(self.Url_platform[1]) , "date_update": str(date.today())})
        self.CSTrack_platforms_projects.remove({"Url":str(self.Url_platform[1])})
        self.collection.remove({"Url":str(self.Url_platform[1])})
        
    def language(self, Id, text):

        lng = detect(str(text))
        return self.check_data_cleaning.find({"Id":4}, {"Languages":1, "_id":0})[0].get("Languages")[lng] 

    def retrieve_projects (self, Id):

        project =self.collection_pla.find({"Id": Id})[0]
    
        #CHECK IF WORK
        if str(self.collection_pla.find({"Id":Id})[0].get("Load")) == 'yes' and str(self.collection_pla.find({"Id":Id})[0].get("Projects load")) == 'Automatic':
            for x in self.CSTrack_platforms_projects.find({"Id": Id}):
                Id = list(x.values())[1]
                Url = list(x.values())[2]
                Name = list(x.values())[3]
                country = list(x.values())[4]
                wp2_id = list(x.values())[6]

                self.initialUrl = Url
                language = self.collection_pla.find({"Id":Id})[0].get("Language")

                #If it does not exist, then continue. if it exists then do nothing and check the next one
                if self.collection_proj.find({ "Url platform": Url }).count() == 0 :  #self.CSTrack_projects_descriptors.find({ "Url platform": Url }).count() == 0 or 
                    
                    #Initialize lists, start the lists of descriptors
                    self.descriptors_definition ()

                    #Execute the process, Id: 13 is different
                    if str(Id) == '13': 
                        
                        for i in ['','/about/research' , '/about/team', '/about/education', '/about/results' , '/about/faq' ]: #  
                            
                            if i == '' :
                                new_url = str(Url)
                                Class = str(list(project.get("ProjClassName"))[0])
                            else:
                                Class = str(list(project.get("ProjClassName"))[1])
                                new_url = str(Url)+i

                            
                            #Start the process
                            self.execute_process( Id, new_url, project, Name, country, Class)
                    else:
                        #Get ClassName and iterate
                        Class = project.get("ProjClassName")
                        #Start the process
                        self.execute_process( Id, Url, project, Name, country, Class)

                    #Call for dictionary conversion and insert or update into database
                    self.dictionaryConversion(Id, country, wp2_id, language)

                    #Insert new
                    self.insert_descriptors()

    def execute_process(self, Id, Url, project, Name, country, Class):

        #Get driver: Add ?tab=about for '111' link
        if str(Id) == '111':
            LastUrl = str(Url)+"?tab=about"

            #Call def get_driver
            self.get_driver(LastUrl, Id)
        else:
            #Call def get_driver
            self.get_driver(Url, Id)   
            time.sleep(5)


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

    def pruebas(self, Id, projectUrl, Name, Plat_country, className):

        
        #Initialize lists
        self.descriptors_definition ()

        self.projects_descriptors(Id, projectUrl, Name, Plat_country, className)

        #Close
        time.sleep(5)
        self.driver.close()

        #Call for dictionary conversion and insert or update into database
        self.dictionaryConversion(Id, country, Id, language)


           
#Populate the database with url platforms #apper
scraper = Scraper()

#Pendiente de decidir como leer span y div
#scraper.projects_descriptors('66','https://biocollect.ala.org.au/acsa/project/index/f300d3ac-3024-48a3-a8b6-229d075ff276', 'DK', 'AUT', 'pill-content')

#scraper.pruebas('111','https://www.inaturalist.org/projects/intersex-ducks', 'iNaturalista', 'iNaturalista','', 'stracked')


#scraper.get_Cs_Platform(40, 'Instant wild', 'https://instantwild.zsl.org/projects', '', '','', '','World wide', 'Biodiversity platform', 'English', 'Manual', 'Automatic')
#scraper.get_Cs_Platform_Projects(60, 'https://www.barcelona.cat/barcelonaciencia/es/proyectos-ciencia-ciudadana', '', '','', '//*[@id="article-content"]/article[2]/div[2]/div[9]/ul/li[5]/a/i','World wide')
scraper.retrieve_projects(17)
#scraper.retrieve_platforms (17)
#scraper.pruebas(13, 'https://www.zooniverse.org/projects/ssilverberg/disk-detective/about/team', 'test', 'World', 'columns-container')


#Loop to read for each project in platform the tags informed
'''for x in collection.find():
    projects = []
    res_dct = {}
    #print(list(x.values())[1])
    getInfoProjects(list(x.values())[1])    #Retrieve all tag informed
    collection_proj.insert_one(dictionaryConversion(projects))  #For the dictionary created from a list, insert each one in database'''

