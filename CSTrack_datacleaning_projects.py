import time
from pymongo import MongoClient
from datetime import date

class Datacleaning:
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

        self.CSTrack_platform_projects = db.CSTrack_platforms_projects
        self.CSTrack_projects_descriptors = db.CSTrack_projects_descriptors

        self.STG_projects_pro_list = db.STG_projects_pro_list

        self.CSTrack_config = db.CSTrack_config  #Projects information
        self.log_error = db.CSTrack_logerror #Store error for datacleaning
        self.check_data_cleaning = db.CSTrack_check_data_cleaning #Check number of projects or other conditions
        

    def Check_num_projects(self, Id):

        #0: Get the number of projects loaded
        num_projects = self.CSTrack_platform_projects.find({"Id":Id}).count()

        #1: check if the number of projects is equal or greater to the previous number
        
        #  CAMBIAAAAR     Retrieve the number of projects stored in a dictionary in document
        list_values = self.check_data_cleaning.find({"Id":2,"List":{"$elemMatch":{"Id":Id}}})[0].get("List") 

        #For each value, retrieve a tuple with the different values
        for i in range(0, len(list_values)):
            if list_values[i].get('Id') == Id:
                for sub, value in list_values[i].items(): 
                    if sub == 'number':
                        num_stored = value            

        #Check if number of projects is greater or not of previous exctraction
        if int(num_projects) >= int(num_stored):
            #2: if it is, update the number of projects and the date_update
            #print(f"The project with {Id} has loaded successfully")
            self.check_data_cleaning.update_one({"Id":2, "List":{"$elemMatch":{"Id":Id}}},{"$set":{"List.$.number":num_projects, "List.$.date_update": str(date.today())}})

            self.result = 'OK'

        else:
            #3: if it is not, update log error to inform that the number of projects loaded is lower than the stored in the previous execution 
            self.log_error.insert_one({"Error type": "Number of projects with descriptors in projects_pro_list", "Id": Id, "Error": "The project with Id " + str(Id) + " has loaded only " + str(num_stored) + " check the URL ", "date_update": str(date.today())})

            self.result = 'FAIL'
    
    def Check_descriptors(self, Id):

        for x in self.STG_projects_pro_list.find({"Plat Id": str(Id)}):

            name = str(list(x.values())[1])

            #Remove null values
            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":""}})

            #Remove @ in description
            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'@'}}})

            #Remove *, ',' in description
            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['*', ',']}}})

            #Remove jvascript message in description
            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'javascript:'}}})


            if str(Id) == '13':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['Join in', 'Get started', 'Learn more', 'Volunteers', 'Classifications', \
                    'Subjects', 'Completed Subjects']}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'STATISTICS'}}})

                #Classify webpages                
                
                if self.STG_projects_pro_list.find({"TITLE":name}, {"WEB":1, "_id":0})[0].get("WEB") :

                    for i in self.STG_projects_pro_list.find({"TITLE":name}, {"WEB":1, "_id":0})[0].get("WEB") :

                        if '/talk' in i:
                            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":i}})
                            self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"COMMENTS":i}})

                        elif '/stats' in i:
                            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":i}})
                            self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"STATUS":i}})

                        elif '/classify' in i:
                            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":i}})
                            self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"TOOLS AND MATERIALS":i}})

                        elif '/about' in i:
                            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":i}})
                            self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"OTHER ON-LINE RESOURCES":i}})
            
            elif str(Id) == '180':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://citizenscience.dk/portfolio/'}}})
                
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$in":['https://gravatar.com/site/signup/', 'https://akismet.com/privacy/']}}})

            elif str(Id) == '67':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['Menu', 'Sluit menu', 'Follow us', 'Partners', 'Ewi Vlaanderen', \
                    'RVO Society', '	 minskyString.search.closeLabel', '	 minskyString.search.triggerLabel']}}})

            elif str(Id) == '184':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.iedereenwetenschapper.be/tags-overview/'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.iedereenwetenschapper.be/newsletter'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.iedereenwetenschapper.be/bio'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.iedereenwetenschapper.be/meld-je-project'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.iedereenwetenschapper.be/voor-onderzoekers'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.iedereenwetenschapper.be/over-ons'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.iedereenwetenschapper.be/search-for-project'}}})

                #Move category to type 
                for i in self.STG_projects_pro_list.find({"TITLE":name}, {"WEB":1, "_id":0})[0].get("WEB") :

                        if '/category-overview/' in i:
                            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":i}})
                            self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"CATEGORY":i}})

            elif str(Id) == '111':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['Acerca de', 'Ayuda', 'Foro', 'Prensa', 'Nuestro blog', \
                    'Directrices de la comunidad', 'Términos del servicio', 'Privacidad', \ 
                    '/Enero/', '/EDT/', '/Febrero/', '/Marzo/', '/Abril/', '/Mayo/', '/Junio/', '/Juloi/', '/Agosto/', '/Septiembre/', '/Octubre/'\
                    '/Noviembre/', '/Diciembre/']}}})


    def STG_insert_all(self, Id):

        for x in self.collection_proj.find({"Plat Id": str(Id)}):
             
            name = str(list(x.values())[1])

            if self.STG_projects_pro_list.find({'TITLE': name}).count == 0:
                #If project does not exist, then insert it
                self.STG_projects_pro_list.insert(x)
            
            else:
                #If project exists: Remove and insert again. New data will be explored:
                self.STG_projects_pro_list.remove({'TITLE': name})
                self.STG_projects_pro_list.insert(x)

    def FIN_insert_all(self, Id, wp2_id ):

        for x in self.STG_projects_pro_list.find({"Plat Id": str(Id)}):
             
            name = str(list(x.values())[1])

            if self.CSTrack_projects_descriptors.find({'TITLE': name}).count() == 0:

                #If project does not exist, then insert it
                self.CSTrack_projects_descriptors.insert_one(x)
                self.CSTrack_projects_descriptors.update({'TITLE': name},{'$set':{'Wp2 Id':wp2_id}})   #Check!!!
            
            else:

                #If project exists, then check if there is new information
                for i in range(1,len(list(x.values()))):
                    try:
                        #Go through and array and check if the information already exists
                        for j in range(0, len(list(x.values())[i])) :
                            #Read all the information of each descriptor (array) and check if exist. If not, insert.
                            self.CSTrack_projects_descriptors.update({"TITLE":name},{"$addToSet":{str(list(x)[i]):str(list(x.values())[i][j])}})
                    except:
                        pass
                
            
            

    def Datacleaning_projects(self, Id2):

        for x in self.collection_pla.find({"Id": Id2}):
            Id = list(x.values())[1]
            '''Url = list(x.values())[2]
            Name = list(x.values())[3]'''
            wp2_id = int(self.collection_pla.find({"Id":Id})[0].get("Wp2 Id"))

            #if is informed as to be loaded
            if str(self.collection_pla.find({"Id":Id})[0].get("Load")) == 'yes':
                #check the number of projects and if it is a correct value. Insert it if all correct
                self.Check_num_projects (Id) 

                if self.result == 'OK':

                    #Step to create STG to clean dat
                    self.STG_insert_all(Id)

                    #Clean data in STG step
                    self.Check_descriptors(Id)

                    #Insert data
                    self.FIN_insert_all(Id, wp2_id)
    
                
data_cleaning = Datacleaning()
#data_cleaning.check_num_projects(9, "valores")
data_cleaning.Datacleaning_projects(184)