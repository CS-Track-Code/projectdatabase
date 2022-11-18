from datetime import date

from langdetect import detect
import requests
import json
import re

import pyinaturalist
from pyinaturalist.node_api import get_observation
from pyinaturalist.node_api import get_projects
from pyinaturalist.rest_api import get_access_token


from CSTrack_Mongo_conn import connection
from pymongo import MongoClient

import urllib3

class APIProjects:
    def __init__(self):
        #Mongodb connection
        self.conn = MongoClient(connection())

        #Mongodb database and repository
        db = self.conn.CSTrack

        #Collections
        self.collection_pla =  db.platforms_pla_list #Platforms
        self.collection_proj = db.projects_pro_list  #Projects information
        self.CSTrack_projects_descriptors = db.CSTrack_projects_descriptors


        self.check_data_cleaning = db.CSTrack_check_data_cleaning #Check number of projects or other conditions


    def EU_CS_Platform_API(self, plat_id, country):

        API_URL = "https://eu-citizen.science/api/projects/"

        TAG_RE = re.compile(r'<[^>]+>')

        urllib3.disable_warnings()

        response = requests.get(API_URL,  verify=False).json()

        for i in range(len(response)):
            #For each project define empty dictionaries and arrays
            dic = {}
            values_topic = []
            values_status = []
            values_funding = []
            values_keywords = []

            #Select each project
            value = response[i]
            print(value)
            #Start assigning elements
            dic['TITLE'] = value['name']

            for i in value['keywords']:
                values_keywords.append(i['keyword'])

            #For description remove tags elements
            aim_desc = TAG_RE.sub('', value['aim'])
            values_desc = TAG_RE.sub('', value['description'])
            dic['DESCRIPTION'] = [aim_desc, values_desc, {"Keywords": values_keywords}]

            if value['status']['status']:
                dic['STATUS'] = value['status']['status']

            if value['topic']:
                for i in value['topic']:
                    values_topic.append(i['topic'])
                dic['TOPICS'] = values_topic
            
            if value['start_date']:
                dic['START DATE'] = value['start_date']
            
            if value['end_date']:
                dic['END DATE'] = value['end_date']
            
            if value['url']:
                dic['WEB'] = [value['url']]
            
            if value['latitude']:
                dic['LATITUDE'] = value['latitude']
            
            if value['longitude']:
                dic['LONGITUDE'] = value['longitude']
            
            if value['country']:
                dic['COUNTRY'] = value['country']
            
            values_images = [value['image1'], value['imageCredit1'], value['image2'], value['imageCredit2'], value['image3'], value['imageCredit3']]
            dic['IMAGE'] = list(filter(None, values_images))

            #For methodology remove tags elements
            if value['howToParticipate']:
                values_methodology = TAG_RE.sub('', value['howToParticipate'])   
                dic['METHODOLOGY'] = [values_methodology]
            try:
                if value['ParticipationTask']:
                    values_methodology = TAG_RE.sub('', value['ParticipationTask'])   
                    dic['METHODOLOGY'].append(values_methodology)
            except:
                pass

            #This element only inform if project can be developed online
            if value['doingAtHome']:
                dic['DEVELOPMENT SPACE'] = ["Doing at home: "+ str(value['doingAtHome'])]

            #For tools and materials remove tags elements
            if value['equipment']:
                values_tools = TAG_RE.sub('', value['equipment'])        
                dic['TOOLS AND MATERIALS'] = [values_tools]

            try:
                if value['fundingProgram']:
                    dic['INVESTMENT'] = [value['fundingBody']['body'], value['fundingProgram']]
                else:
                    dic['INVESTMENT'] = [value['fundingBody']['body']]
            except TypeError: # If value['fundingBody']['body'] doesn't work, then check if value['fundingProgram'] exist
                if value['fundingProgram'] :
                    dic['INVESTMENT'] = [value['fundingProgram']]
            
            #For main program or person in charge
            try:
                if value['mainOrganisation']['name']:
                    dic['MAIN PROGRAM OR PERSON IN CHARGE'] = value['mainOrganisation']['name']    
            except:
                continue   

            #For email
            if value['mainOrganisation']['contactPointEmail']:
                dic['MAIL'] = value['mainOrganisation']['contactPointEmail']   

            dic['PLATFORM UPDATE DATE'] = value['dateCreated']

            #Data management information
            dic['Plat Id'] = str(plat_id)
            dic['Insert date'] = str(date.today())
            dic['Plat country'] = str(country)
            dic['Url platform'] = 'https://eu-citizen.science/projects'

            try:
                dic['Language'] = self.language(plat_id, values_desc)
            except:
                dic['Language'] = 'English'

            if self.collection_proj.find({ "TITLE": dic['TITLE'] }).count() == 0:
                self.collection_proj.insert_one(dic) 


    def language(self, Id, text):

        lng = detect(str(text))
        return self.check_data_cleaning.find({"Id":4}, {"Languages":1, "_id":0})[0].get("Languages")[lng] 

    def API_retrieve_projects(self):

        plat_id = "17"
        country = "EU"

        self.EU_CS_Platform_API(plat_id, country)   
 
if __name__ == "__main__":

    API_projects = APIProjects()
    API_projects.API_retrieve_projects()
