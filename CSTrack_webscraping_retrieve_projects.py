import bs4, requests, pymongo, pprint, requests, time, re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import date
from langdetect import detect
from CSTrack_Mongo_conn import connection


from pymongo import MongoClient

class ScraperProjects:
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
        self.check_data_cleaning = db.CSTrack_check_data_cleaning #Check number of projects or other conditions

        self.CSTrack_projects_descriptors_NO_EU = db.CSTrack_projects_descriptors_NO_EU #Projects out EU



    def get_driver(self, platform_url, Id):
        #Selenium library read: Chromedriver route
        route = 'D:/Users/Miriam/Documents/python/web_scrapping/chromedriver/chromedriver.exe'
        
        #Open chrome
        self.driver = webdriver.Chrome(executable_path= route)
        
        #Get driver Url platform
        self.driver.get(platform_url)

        time.sleep(5)

        if str(platform_url) != str(self.driver.current_url):
            new_Url = str(self.driver.current_url)+"?tab=about"

            #Get new driver Url platform
            self.driver.get(new_Url)

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

    def projects_descriptors(self, Id, project_url, name, plat_country, class_name):

        self.get_elem(class_name)

        # Tag "a" - mail / web / img / social media
        self.get_items(class_name, "a")

        try:
            for item in self.items: 
                if item.get_attribute('href'):

                    if str(Id) == '13':

                        if 'team' in project_url :
                                
                            if item not in self.participants[0:]:   
                                self.participants.append(item.get_attribute('href'))
                        else:
                            self.check_descriptors(item.get_attribute('href'))
                    else:
                        self.check_descriptors(item.get_attribute('href'))

        except:
            pass 
          

        if int(Id) == 193:
            # Tag "div" - description + others

            self.get_items(class_name, "h1")
            print(self.items)

            for item in self.items:
                
                print(item.text.strip())
    

            self.get_items(class_name, "h2")
            
            for item in self.items:
                text2 = item.text.split('\n')
                
  
        elif int(Id) == 17:
            # Tag "p" - description + others
            self.get_items(class_name, "class")

        elif int(Id) == 32:
            #¡¡¡¡REVISAR ESTO PORQUE NO HAY MANERA!!!!
            # Tag "p" - description + others
            self.get_items(class_name, "br")

            try:
                for item in self.items: 
                    self.check_descriptors(item.text)
            except:
                pass 

            # Tag "p" - description + others
            self.get_items(class_name, "p")
            
            try: 
            
                for item in self.items:
                    self.check_descriptors(item.text.replace('\n', ' '))

            except:
                pass

        elif int(Id) == 174:
            
            self.get_items(class_name, 'div')
            
            text_list = self.items[0].text.split('\n')
            description = ''

            for i in text_list:
                #For all the values in a list, find all the titles (upper case) and description (lower case)
                if i.isupper() :
                    if description :
                        text = text + ' ' + description
                        self.check_descriptors(text)
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
            self.get_items(class_name, "p")
            
            try:

                #Specific behaviour for Id:184
                if str(Id) == '184':
                    
                    item = self.items[0]
                    self.check_descriptors(item.text)

                    for i in range(1,len(self.items),2):
                        item = self.items[i]
                        desc = self.items[i+1]
                        #Concatenar título y texto
                        self.check_descriptors(item.text+" : "+desc.text)
                
                else:                      
                    for item in self.items:
                        #Two tabs one for The team and other for resources shoud be stored in participants and results lists
                        if str(Id) == '13':

                            if 'team' in project_url :
                                
                                if item not in self.participants[0:]:   
                                    self.participants.append(item.text)

                            elif 'results' in project_url:
                                if item not in self.participants[0:]:    
                                     self.results.append(item.text)
                            
                            elif 'faq' in project_url:
                                if item not in self.methodology[0:]:    
                                     self.methodology.append(item.text)
                            
                            elif 'education' in project_url:
                                if item not in self.methodology[0:]:    
                                     self.resources.append(item.text)

                            else:
                               self.check_descriptors(item.text.replace('\n', ' '))
                        else:
                            self.check_descriptors(item.text.replace('\n', ' '))
                
            except:
                pass
            

            # Tag "table" - description + others
            self.get_items(class_name, "tr")

            try:
                for item in self.items: 
                    self.check_descriptors(item.text.replace('\n', ' ') )
            except:
                pass

            # Tag "list" - description + others
            self.get_items(class_name, "li")

            try:
                for item in self.items: 

                    if str(Id) == '13':

                        if 'team' in project_url :
                                
                            if item not in self.participants[0:]:   
                                self.participants.append(item.text)
                        else:
                            self.check_descriptors(item.text)
                    else:
                        self.check_descriptors(item.text.replace('\n', ' ') )
                    
            except:
                pass


            # Tag "span" - description + others
            self.get_items(class_name, "span")

            try:
                for item in self.items:

                    if str(Id) == '13':

                            if 'team' in project_url :
                                #No store this information, we have it as a list
                                pass

                            else:
                               self.check_descriptors(item.text)
                    else:
                        self.check_descriptors(item.text)

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

                self.get_items(class_name, "h1")
                if self.items: #If not empty
                    for item in self.items:
                        if item.text and item.text not in self.title[0:] :    #if tittle is informed and is not in project list                        
                            self.title.append(item.text)

                else: #If empty h1 then check h2
                    self.get_items(class_name, "h2")
                    if self.items:  #If not empty
                        for item in self.items:
                            if item.text and item.text not in self.title[0:] :    #if tittle is informed and is not in project list                        
                                self.title.append(item.text)
                            
                            #h2 retrieve important information
                            if int(Id) == 63:
                                self.check_descriptors(item.text.replace('\n', ' ') ) 

                    else:   #If empty get Project Name from platform extraction
                        self.title.append(name)
                        
                        print(name)
        except:
            self.title.append(name)

        try:
            self.get_items(class_name, "h6")
            if self.items and Id == 147 : #If not empty
                if item.text and item.text not in self.main[0:] :    #if tittle is informed and is not in project list                        
                    self.main.append(item.text)
        except:
            pass

        #some projects inform TITLE with "Estadísticas del evento"
        if int(Id) == 60:
            if "Otros proyectos" in self.title[1] :
                self.title.pop()
                self.title.append(name)
        elif int(Id) == 66:
            if "Contenido" in self.title[1] :
                self.title.pop()
                self.title.append(name)
        
        if  int(Id) == 63 or int(Id) == 13:
            self.title = ['TITLE']
            self.title.append(name)


        #After complete all the lists, Platform Id, Platform country and current date is updated
        self.Id_plat = ["Plat Id", Id]
        self.country_plat = ["Plat country", plat_country]
        self.insert_date = ["Insert date", date.today()]
        self.url_platform = ["Url platform", self.initial_url]

    #Check text extracted conditions
    def check_descriptors(self, value):

       
        if ('www.' in str(value) or 'http' in str(value)) and ' ' not in str(value):
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
            elif '@' in str(value):
                #print(item.get_attribute('href'))
                if value and value not in self.mail[0:] :    #if tittle is informed and is not in project list
                    self.mail.append(value)
                    self.description.append(value)
            else:
                self.description.append(value)


    #Convert a list as a dictionary
    def dictionary_conversion(self, Id, country, wp2_id, language): 

        #Create a list of lists to read automatically the data retrieved
        self.dictionary = [tuple(self.title),tuple(self.web), tuple(self.social_media), tuple(self.mail), 
        tuple(self.description), tuple(self.Id_plat), tuple(self.country_plat), tuple(self.insert_date), 
        tuple(self.app), tuple(self.images), tuple(self.resources), tuple(self.geo), tuple(self.status), tuple(self.methodology), 
        tuple(self.start_date), tuple(self.investment), tuple(self.topic), tuple(self.time), tuple(self.ages), tuple(self.dedication) ,
        tuple(self.space), tuple(self.update_date), tuple(self.url_platform), tuple(self.main), tuple(self.participants), tuple(self.objectives),
        tuple(self.tools), tuple(self.num_members), tuple(self.end_date), tuple(self.results)]

        #Check if tittle is ¡Eso no existe!
        if self.title[1] == "¡Eso no existe!" or "Se ha interrumpido la conexión" in self.title[1]:
            self.check_errors()
        else:
            print(self.dictionary)

            self.desc_dict = {}
            self.lista = self.dictionary[0]
             
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
        self.log_error.insert_one({"Error type": "Project does not exist", "Id": str(self.Id_plat[1]), "Error": "Check the URL: " + str(self.url_platform[1]) , "date_update": str(date.today())})
        self.CSTrack_platforms_projects.remove({"Url":str(self.url_platform[1])})
        self.collection.remove({"Url":str(self.url_platform[1])})
        
    def language(self, Id, text):

        lng = detect(str(text))
        return self.check_data_cleaning.find({"Id":4}, {"Languages":1, "_id":0})[0].get("Languages")[lng] 

    def retrieve_projects (self, Id):
        
        #Load projects from one platform by Id or all the projects stored in CSTrack_platforms_projects
        if Id:
            project_list = self.CSTrack_platforms_projects.find({"Id": int(Id), "load_date": str(date.today())}) #str(date.today())
        else:
            project_list = self.CSTrack_platforms_projects.find({"load_date": str(date.today())}) #str(date.today())

        for x in project_list:
            
            #Project platform Id
            Id = x['Id']

            if str(self.collection_pla.find({"Id":Id})[0].get("Load")) == 'yes' and str(self.collection_pla.find({"Id":Id})[0].get("Projects load")) == 'Automatic':
                
                project = self.collection_pla.find({"Id": Id})[0]

                #Platforms projects elements
                Url = x['Url']
                name = x['Name']
                country = x['Country']
                wp2_id = x['Wp2 Id']
                self.initial_url = Url

                #Identify language
                language = self.collection_pla.find({"Id":Id})[0].get("Language")

                #If it does not exist in the final list, then continue. if it exists then do nothing and check the next one
                if self.CSTrack_projects_descriptors.find({ "Url platform": Url }).count() == 0 and self.collection_proj.find({ "Url platform": Url }).count() == 0:  #self.CSTrack_projects_descriptors.find({ "Url platform": Url }).count() == 0 or 
                    
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
                            self.execute_process( Id, new_url, project, name, country, Class)
                    else:
                        #Get ClassName and iterate
                        Class = project.get("ProjClassName")
                        #Start the process
                        self.execute_process( Id, Url, project, name, country, Class)

                    #Call for dictionary conversion and insert or update into database
                    self.dictionary_conversion(Id, country, wp2_id, language)

                    #Insert new
                    self.insert_descriptors()

    def execute_process(self, Id, Url, project, name, country, Class):

        #Call def get_driver
        self.get_driver(Url, Id)   
        time.sleep(5)


        #Get elements and all the information for each descriptor
        if Class:
            #Check if a list and iterate, if not, then pass Class element
            if isinstance(Class, str) :
                self.projects_descriptors(Id, Url, name, country, Class)
                            
            else:
                                                        
                for i in list(Class):
                    self.projects_descriptors(Id, Url, name, country, i)

        else:
            self.projects_descriptors(Id, Url, name, country, '')

        #Close
        time.sleep(5)
        self.driver.close()


    def move(self):
        for x in self.CSTrack_projects_descriptors.find({"Plat Id": "111"}): 
                    
            url = x["Url platform"]
            
                
            #If project does not exist, then insert it
            self.CSTrack_projects_descriptors_NO_EU.insert(x)
            self.CSTrack_projects_descriptors.remove({'Url platform': url})



if __name__ == "__main__":
    
    scraper = ScraperProjects()
    scraper.retrieve_projects('')