from datetime import date

import pyinaturalist
from pyinaturalist.node_api import get_observation
from pyinaturalist.node_api import get_projects
from pyinaturalist.rest_api import get_access_token

from CSTrack_Mongo_conn import connection
from pymongo import MongoClient

class APIProjects:
    def __init__(self):
        #Mongodb connection
        self.conn = MongoClient(connection())

        #Mongodb database and repository
        db = self.conn.CSTrack

        #Collections
        self.collection_pla =  db.platforms_pla_list #Platforms
        self.collection_proj = db.projects_pro_list  #Projects information

    def inat_API(self, plat_id, country):

        pyinaturalist.user_agent = "CSTrack"

        #Dictionary with elements and titles
        dict_elements = {'title': 'TITLE', 'description': 'DESCRIPTION',  'icon': 'IMAGE', 'header_image_url':'IMAGE', \
            'icon_file_name': 'IMAGE', 'project_type': 'TOPICS', 'latitude': 'LATITUDE', \
            'longitude':'LONGITUDE', 'location': 'GEOGRAPHICAL LOCATION', 'id':'Url platform', 'admins': 'PARTICIPANTS PROFILE' }
        #Initialize empty dictionary list, page_elem
        dic_proj = {}
        image = []
        page_elem = 0

        try:
            # Get all projects from all pages
            while True:
                    
                page_elem +=  1
                    
                response = get_projects(
                    #Center of Europe + 3000 km radius (5600km aprox. long.)
                    lat = 54.52596,
                    lng = 15.255119,
                    radius = 3000,
                    per_page = 200,
                    page = page_elem
                )

                project_info = response['results']

                #For each project in page (max. 200)
                for p in project_info:
                    #Get the tittle to write the dictionary and element of dictionary
                    for key, value in dict_elements.items():
                        #If there ir information
                        if p[key]:
                            #Some elements are stored without list
                            if ('title' in key) or ('latitude' in key) or ('longitude' in key) or ('location' in key):
                                        
                                dic_proj[value] =  p[key]

                            #Image comes from two elements, list is used to 
                            elif 'IMAGE' in value:
                                image.append(p[key])

                            #Create the Project URL by text+id
                            elif 'Url platform' in value:
                                    
                                dic_proj[value] = str('https://www.inaturalist.org/projects/'+str(p[key]))
                                
                            #Some elements are stored in a list
                            else:
                                dic_proj[value] =  [p[key]]
                            
                    #Image comes from two elements, list is used to 
                    dic_proj['IMAGE'] = image
                    dic_proj['Plat Id'] = str(plat_id)
                    dic_proj['Insert date'] = str(date.today())
                    dic_proj['Plat country'] = str(country)

                    if self.collection_proj.find({ "TITLE": dic_proj['TITLE'] }).count() == 0:
                        self.collection_proj.insert_one(dict(dic_proj)) #dict(dic_proj)
            
        except:
            pass

    def API_retrieve_projects(self):

        project_list = self.collection_pla.find({"Projects load": "API"})

        for x in project_list:

            plat_id = list(x.values())[1]
            country = list(x.values())[8]   

            self.inat_API(plat_id, country)   



if __name__ == "__main__":

    API_projects = APIProjects()
    API_projects.API_retrieve_projects()

