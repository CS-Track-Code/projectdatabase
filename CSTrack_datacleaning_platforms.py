import time
from pymongo import MongoClient
from datetime import date
from CSTrack_Mongo_conn import connection


class DatacleaningPlatforms:
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
        self.CSTrack_platform_projects = db.CSTrack_platforms_projects

        self.log_error = db.CSTrack_logerror #Store error for datacleaning
        self.check_data_cleaning = db.CSTrack_check_data_cleaning #Check number of projects or other conditions


    def check_num_projects(self, Id):

        #0: Get the number of projects loaded
        num_projects = self.collection.find({"Id":Id}).count()

        #1: check if the number of projects is equal or greater to the previous number
        try:
            #Retrieve the number of projects stored in a dictionary in document
            list_values = self.check_data_cleaning.find({"Id":1,"List":{"$elemMatch":{"Id":Id}}})[0].get("List") 

        
            #For each value, retrieve a tuple with the different values
            for i in range(0, len(list_values)):
                if list_values[i].get('Id') == Id:
                    for sub, value in list_values[i].items(): 

                        if sub == 'number':
                            num_stored = value   
        except:
            self.log_error.insert_one({"Error type": "Id not found in list of CSTrack_check_data_cleaning", "Id": Id, "date_update": str(date.today())})
            pass
         

        #Check if number of projects is greater or not of previous exctraction
        if int(num_projects) >= int(num_stored):
            #2: if it is, update the number of projects and the date_update
            self.check_data_cleaning.update_one({"Id":1, "List":{"$elemMatch":{"Id":Id}}},{"$set":{"List.$.number":num_projects, "List.$.date_update": str(date.today())}})
            
        else:
            self.check_data_cleaning.update_one({"Id":1, "List":{"$elemMatch":{"Id":Id}}},{"$set":{"List.$.number":num_projects, "List.$.date_update": str(date.today())}})

            #3: if it is not, update log error to inform that the number of projects loaded is lower than the stored in the previous execution 
            self.log_error.insert_one({"Error type": "Number of projects link from platform loaded in projects_pla_list", "Id": Id, "Error": "The project with Id " + str(Id) + " has loaded only " + str(num_stored) , "date_update": str(date.today())})
 

    def check_links (self, Id, Name, Url, country, wp2_id):

        if self.CSTrack_platform_projects.find({ "Url": Url }).count() == 0: 
            if Id == 9:

                if  '/projektarchiv' in Url and Url != 'https://www.citizen-science.at/projekte/ein-neues-projekt-listen':
                  
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)
            
            elif Id == 180:
                
                if  Name != 'Projekter' and Name != 'Tilpas' and Name != 'Older projects' and Name != 'Log ind' and Name != 'Log in now.':
                  
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 35:
                
                if  Name != 'Actualités' and Name != 'Agenda' and Name != 'Agenda' and Name != 'Présentation' and \
                    Name != 'Du citoyen à la recherche scientifique' and Name != 'Contactez-nous' and Name != 'Mentions légales et crédits' and \
                    Name != 'Plan du site' and Name != 'En savoir plus' and Name!= 'Voir toutes les vidéos' and 'Gestionnaires' not in Name and \
                    Name != 'Pour tous' and '/actualites/' not in Url and '/agenda/' not in Url and '/media-video/' not in Url and Name != "Offres d'emploi" and \
                    Name != 'Bibliographie' and Name != 'Accès aux données' and '.frhttp://' not in Url:

                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 65:
                if  Url != None :
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 111:
                if  Url != 'https://www.inaturalist.org/projects/new' and 'https://www.inaturalist.org/projects/browse?page=' not in Url:

                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 30:
                if  'https://observations.be/projects/?sort' not in Url and '/apply/' not in Url:

                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 32:
                if  Url != 'http://www.citizen-science-germany.de/citizen_science_germany_projekte.html':

                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 33:
                if  Name != 'weiterlesen...' and Url != 'https://www.uni-muenster.dehttps://www.uni-muenster.de/AFO/CS/mitforschen/lateralitaet.html':

                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)
            
            elif Id == 34:
                if  Name != 'Présentation' and Name != 'Du citoyen à la recherche scientifique' and Name != 'Voir toutes les vidéos'\
                    'http://www.vigienature.frhttp://www' not in Url and Name != 'Actualités' and \
                    'http://www.vigienature.fr/fr/media-video/' not in Url and Name != 'Plan du site' and \
                    '/agenda/' not in Url and Name != 'Contactez-nous' and Name != 'Mentions légales et crédits' and \
                    Name != 'Plan du site' and Name != 'En savoir plus' and Name !=  'Pour tous'  and  Name != 'Naturalistes' and \
                    'gestionnaires' not in Url  and  Name != 'Second passage du STOC' and '/actualites/' not in Url  :

                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 11:
                if Name != 'View Projects' and Name != 'Add or Edit a Project':
                     #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 128:
                if Name != 'JOIN A PROJECT' and Name != 'Expeditions' and '/default.aspx' in Url and Name != 'Earthwatchers': 
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 211:
                if Name != 'DE' and Name != 'Sitemap' and Name != 'Porträt' and Name != 'Projekte' and Name != 'Partner'  and Name != 'Kontakt / Medien' \
                    and Name != 'Dialog Wissen­schaft - Kinder und Ju­gend­liche' and Name != 'Dialog Wissen­schaft - Breite Öf­fent­lich­keit'\
                    and Name != 'Dialog zwischen Akteuren der Wissen­schafts­kom­mu­ni­ka­tion' and  Name != 'Projekte Romandie' and Name != 'Projekte Tessin' \
                    and Name != '2' and Name != '3' and Name != 'Home' and Name != 'Impressum' and Name != 'Suche' \
                    and Name != 'Stiftungsrat' and Name != 'Team' and Name != '#Homeoffice' and Name != 'Jahresberichte' and Name != 'Statuten' and Name != 'Logos' \
                    and Name != 'Medienmitteilungen' and Name != 'Medienschau' and Name != 'Newsletter' and Name != 'BFH Zentrum Energiespeicherung' \
                    and "Das BFH-Zentrum Energiespeicherung und Science et Cité laden zum spielerischen" not in Name: 
                    
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 195:
                if Name != 'Recent first' and Name != '2' and Name != '3' and Name != '4' and Name != '5' and Name != '6' and Name != '7' and Name != 'Previous' :
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 124:
                if Name != 'Read the blog' and Name != 'Citizen science' and ('/content/nhmwww/en/home/' not in Url):

                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 193:
                if Name != 'Add your project' and Name != 'My projects' :

                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 60:
                if Name != 'Inici' and Name != 'Contacto' and Name != 'Decálogo' :
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 62:
                if Name != 'ENG' and Name != 'ESP' and Name != 'CAT' :
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 40:
                if Name != 'Disclaimer' or Name != 'Supporters' or Name != 'projects' or Name != 'News7' or Name != 'Profile' :
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)

            elif Id == 63:
                if Name != 'next ›' and Name != '‹ previous':
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)
            
            elif Id == 61:
                if Name != 'Ciencia ciudadana' and Name != '#CienciaDirecta' and Name != 'Perfil del contratante' \
                    and Name != 'Patronos' and Name != 'Contacto' and Name != 'Más información':
                    #If is a correct value insert
                    self.insert_information(Id, Name, Url, country, wp2_id)


            else:
                #If is a correct value insert
                self.insert_information(Id, Name, Url, country, wp2_id)
    
    def insert_information(self, Id, Name, Url, country, wp2_id):

        self.CSTrack_platform_projects.insert_one({'Id': Id, 'Url':Url, 'Name': Name, 'Country':country, 'load_date': str(date.today()), 'Wp2 Id': wp2_id }) #insert in mongodb database


    def Datacleaning_platforms(self): #, Id2
        #check the number of projects and if it is a correct value. Insert it if all correct
        
        for x in self.collection.find(): #{"Id": Id2}

            Id = x['Id']
            Url = x['Url']
            Name = x['Name']
            country = x['Country']

            wp2_id = int(self.collection_pla.find({"Id":Id})[0].get("Wp2 Id"))

            try:

                self.check_num_projects(Id) #Id2


                #if is informed as to be loaded
                if str(self.collection_pla.find({"Id":Id})[0].get("Load")) == 'yes' and str(self.collection_pla.find({"Id":Id})[0].get("Platform load")) == 'Automatic' :
                    
                    #Check if the link is a correct value to insert it in the document
                    self.check_links (Id, Name, Url, country, wp2_id)
            except:

                pass
                

if __name__ == "__main__":

    data_cleaning = DatacleaningPlatforms()
    data_cleaning.Datacleaning_platforms()