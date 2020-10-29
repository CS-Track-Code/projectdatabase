from pymongo import MongoClient

class InsertPlatform:
    def __init__(self):
        #Mongodb connection
        self.conn = MongoClient(connection())

        #Mongodb database and repository
        db = self.conn.CSTrack

        #Collections
        self.collection_pla =  db.platforms_pla_list #Platforms
    
    def get_Cs_Platform(self, Id, Name, platformUrl, annexed, check, className, buttonName, country, type, language, platform_load, projects_load, edu):

        if self.collection_pla.find({ "Url": platformUrl }).count() == 0: #Check if the url is in database

            self.collection_pla.insert_one({'Id': Id, 'Name':Name, 'Url':platformUrl, 'annexed': annexed, 'check': check, \
                'className': className, 'buttonName': buttonName, 'Country':country, 'ProjClassName': '', 'Load': 'yes',  \
                'Platform load': platform_load, 'Projects load': projects_load, 'Type': type, 'Wp2 Id':Id, 'Language': language, 'Edu': edu })

#Populate the database with url platforms #apper
insert = InsertPlatform()

insert.get_Cs_Platform(40, 'Instant wild', 'https://instantwild.zsl.org/projects', '', '','', '','World wide', 'Biodiversity platform', 'English', 'Manual', 'Automatic', 'yes')




