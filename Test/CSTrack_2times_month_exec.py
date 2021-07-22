from CSTrack_webscraping_retrieve_platforms import ScraperPlatforms
from CSTrack_datacleaning_platforms import DatacleaningPlatforms

from CSTrack_webscraping_retrieve_projects import ScraperProjects
from CSTrack_datacleaning_projects import DatacleaningProjects

import sys
from datetime import date

from CSTrack_Mongo_conn import connection
from pymongo import MongoClient


class Scraper:
    def __init__(self):
        #Mongodb connection
        self.conn = MongoClient(connection())

        #Mongodb database and repository
        db = self.conn.CSTrack

        #Collections
        self.collection = db.projects_pla_list   #Projects from platforms
        self.collection_proj = db.projects_pro_list  #Projects information
        self.log_error = db.CSTrack_logerror #Store error for datacleaning

        self.CSTrack_platforms_projects = db.CSTrack_platforms_projects
        self.CSTrack_projects_descriptors = db.CSTrack_projects_descriptors  #Projects information



    def platforms(self):

        #### RETRIEVE PLATFORMS ###
        #       1. Remove all the projects link retrieved in previous execution from projects_pla_list collection
        #       2. Extract platfrom projects. Use CSTrack_webscraping_retrieve_platforms script.
        #       3. Clean platform projects and insert into CSTrack_platforms_projects

        #1. Remove platform projects loaded in previous execution
        #self.collection.remove({}) 
        #self.log_error.insert_one({"Message type": "Successfully execution", "Message": "projects_pla_list data has been successfully removed" , "date_update": str(date.today())})


        #2. Platforms extraction
        scraper = ScraperPlatforms()

        try:
            scraper.retrieve_platforms ('', '') #Write numerical value to load by Id and write 'manually' to load platforms with buttons
            num_projects = self.collection.find({"load_date": str(date.today())}).count()
            self.log_error.insert_one({"Message type": "Successfully execution", "Message": "Data extracted and inserted "+ str(num_projects) + " projects successfully in projects_pla_list" , "date_update": str(date.today())})

        except Exception as e:
            self.log_error.insert_one({"Message type": "Error execution", "Message": "Error platform extraction in projects_pla_list" + str(e) , "date_update": str(date.today())})

        #3. Platforms data cleaning
        data_cleaning = DatacleaningPlatforms()

        try:
            data_cleaning.Datacleaning_platforms()
            num_projects = self.CSTrack_platforms_projects.find({"load_date": str(date.today())}).count()
            self.log_error.insert_one({"Message type": "Successfully execution", "Message": "Inserted "+ str(num_projects) + " projects successfully in CSTrack_platforms_projects" , "date_update": str(date.today())})
        
        except Exception as e:
            self.log_error.insert_one({"Message type": "Error execution", "Message": "Error platform inserting into CSTrack_platforms_projects" + str(e)  , "date_update": str(date.today())})

    def projects(self):

        #### RETRIEVE PROJECTS INFORMATION ###
        #       1. Extract project information. Use CSTrack_webscraping_retrieve_projects script.
        #       2. Clean project information and insert into CSTrack_platforms_projects

        #1. Remove projects information loaded in previous execution
        #self.collection_proj.remove({}) 
        #self.log_error.insert_one({"Message type": "Successfully execution", "Message": "projects_pla_list data hass been successfully removed" , "date_update": str(date.today())})

        #2. Platforms extraction
        scraper = ScraperProjects()

        try:
            scraper.retrieve_projects('') #Write Id as a str
            num_projects = self.collection_proj.find({"Insert date": str(date.today())}).count()
            self.log_error.insert_one({"Message type": "Successfully execution", "Message": "Data extracted and inserted "+ str(num_projects) + " projects successfully in CSTrack_projects_descriptors" , "date_update": str(date.today())})

        except Exception as e:
            print("Hay un error", e) #Hacer un control de errores por consola + base de datos

        #3. Projects data cleaning 
        data_cleaning = DatacleaningProjects()

        try:
            data_cleaning.Datacleaning_projects('')
            num_projects = self.CSTrack_projects_descriptors.find({"Insert date": str(date.today())}).count()
            self.log_error.insert_one({"Message type": "Successfully execution", "Message": "Inserted "+ str(num_projects) + " projects successfully in CSTrack_projects_description" , "date_update": str(date.today())})
        
        except Exception as e:
            self.log_error.insert_one({"Message type": "Error execution", "Message": "Error platform inserting into CSTrack_projects_description" + str(e) , "date_update": str(date.today())})
        

scraper = Scraper()
#scraper.platforms()
scraper.projects()

