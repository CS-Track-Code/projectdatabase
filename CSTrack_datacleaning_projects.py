import time
from pymongo import MongoClient
from datetime import date
from langdetect import detect
from CSTrack_Mongo_conn import connection


class DatacleaningProjects:
    def __init__(self):
        #Mongodb connection
        self.conn = MongoClient(connection())

        #Mongodb database and repository
        db = self.conn.CSTrack

        #Collections
        self.collection_pla =  db.platforms_pla_list #Platforms
        self.collection = db.projects_pla_list   #Projects from platforms
        self.collection_proj = db.projects_pro_list  #Projects information

        self.CSTrack_platform_projects = db.CSTrack_platforms_projects
        self.CSTrack_projects_descriptors = db.CSTrack_projects_descriptors
        
        #change this collection to execute the data cleaning process
        self.STG_projects_pro_list = db.STG_projects_pro_list
        #db.STG_projects_pro_list
        #db.CSTrack_projects_descriptors

        self.CSTrack_config = db.CSTrack_config  #Projects information
        self.log_error = db.CSTrack_logerror #Store error for datacleaning
        self.check_data_cleaning = db.CSTrack_check_data_cleaning #Check number of projects or other conditions

    def language(self, Id, text):

        lng = detect(str(text))
        return self.check_data_cleaning.find({"Id":4}, {"Languages":1, "_id":0})[0].get("Languages")[lng] 
            

    def Check_num_projects(self, Id):

        #0: Get the number of projects loaded
        num_projects = self.collection_proj.find({"Plat Id":Id}).count() #str(date.today())

        #1: check if the number of projects is equal or greater to the previous number
        
        # Retrieve the number of projects stored in a dictionary in document
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
            self.check_data_cleaning.update_one({"Id":2, "List":{"$elemMatch":{"Id":Id}}},{"$set":{"List.$.number":num_projects, "List.$.date_update": "2021-05-14"}}) #str(date.today())


        else:
            self.check_data_cleaning.update_one({"Id":2, "List":{"$elemMatch":{"Id":Id}}},{"$set":{"List.$.number":num_projects, "List.$.date_update": "2021-05-14"}}) #str(date.today())

            #3: if it is not, update log error to inform that the number of projects loaded is lower than the stored in the previous execution 
            self.log_error.insert_one({"Error type": "Number of projects with descriptors in projects_pro_list", "Id": Id, "Error": "The project with Id " + str(Id) + " has loaded only " + str(num_stored) + " check the URL ", "date_update": "2021-05-14" }) #str(date.today())


    
    def Check_descriptors(self, Id, wp2_id):


        for x in self.STG_projects_pro_list.find({"Plat Id": str(Id), "Insert date": str(date.today()) }): #str(date.today())

            name = str(list(x.values())[1])
            Url = str(x["Url platform"])

            try:

                self.STG_projects_pro_list.update({'TITLE': {"$regex": name}},{'$set':{'Wp2 Id': str(wp2_id)}})   #Check!!!
            except:
                pass

            try:
                #Remove null values
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":""}})

                #Remove @ in description
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'mailto:'}}})

                #Remove *, ',' in description
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['*', ',', '.', ' ', ' ', '','  ', '   ', '     ', '         ',\
                '                                                   ', '                                             ', '                                            '\
                '                                                 ', '                                           ', '    ',  \
                '                                            ', '    ', ', ', '*', 'javascript:', '-'    ]}}})

                #Remove jvascript message in description
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'javascript:'}}})

                #Remove mailto: text
                for i in self.STG_projects_pro_list.find({"MAIL": {'$regex': "mailto:"}, "Insert date": str(date.today()) }, {"_id":0}) : #str(date.today())
                    for x in i['MAIL']:
                        if 'mailto:' in x:
                            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"MAIL":x}})
                            x_replaced = x.replace("%20", "")
                            self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"MAIL":x_replaced}})

            
            except:
                pass

            if str(Id) == '13':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['Join in', 'Get started', 'Learn more', 'Volunteers', 'Classifications', \
                    'Subjects', 'Completed Subjects', 'Blog', 'NQG! Facebook Group', 'See the results or dismiss this message', 'Receive NQG! Updates' ]}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'STATISTICS'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'person is talking about'}}})
                
                self.STG_projects_pro_list.remove({"TITLE":'Organizations', "Plat Id": "13"})
                self.STG_projects_pro_list.remove({"TITLE":'The Project', "Plat Id": "13"})
                self.STG_projects_pro_list.remove({"TITLE":'#TheyFreedThemselves', "Plat Id": "13"})
                self.STG_projects_pro_list.remove({"TITLE":'BUBBLE NEBULAE: IDENTIFY, MARK, AND SIZE', "Plat Id": "13"})
                self.STG_projects_pro_list.remove({"TITLE":'Volunteers Wanted! 75,000 Strong!', "Plat Id": "13"})
                self.STG_projects_pro_list.remove({"TITLE":'De Hoop Nature Reserve', "Plat Id": "13"})
                self.STG_projects_pro_list.remove({"TITLE":'The Notes from Nature Project', "Plat Id": "13"})
                self.STG_projects_pro_list.remove({"TITLE":'Find, classify and measure aurora!', "Plat Id": "13"})
                self.STG_projects_pro_list.remove({"TITLE":{"$regex":"Imagine a galaxy, behind another galaxy"}, "Plat Id": "13"})
                self.STG_projects_pro_list.remove({"TITLE":{"$regex":"Welcome to "}, "Plat Id": "13"})

                if self.STG_projects_pro_list.find({"TITLE":name,"DESCRIPTION":{"$regex":'Looks like this project is out of data at the moment!'}}).count() > 0 :

                    self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Looks like this project is out of data at the moment!'}}})   
                    self.STG_projects_pro_list.update({"TITLE":name},{"$set":{"STATUS":["FINISHED"]}})   


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

                try:
                    #Move category to type 
                    for i in self.STG_projects_pro_list.find({"TITLE":name}, {"WEB":1, "_id":0})[0].get("WEB") :

                            if '/category-overview/' in i:
                                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":i}})
                                self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"CATEGORY":i}})
                except:
                    pass


            elif str(Id) == '37':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['Créé et développé par :','Animé par :','Soutenu par :'\
                    ,'             Actus         ','             Evénements         ','                 Espace Pro             ', 'Soutenu par :', \
                    '                 Espace Pro             ','         Qui sommes-nous?     ','         FAQ     ','         Charte du portail     '\
                    '         Presse     ','         Les conditions générales d*utilisation (CGU)     ','         Contact     ','Open', \
                    'Observatoires participatifs des espèces et de la nature','Menu','×','⇧','i','CARACTÉRISTIQUES','LOCALISATION','ACTUS', \
                    ' Voir le site web', '         Charte du portail     ','         Presse     ', ]}}})
            
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'  Participer  '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'  Ressources  '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Les conditions générales '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'OBSERVATOIRES'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'ÉVÉNEMENTS'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'RESSOURCES'}}})


                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.open-sciences-participatives.org/actus/'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.open-sciences-participatives.org/liste-evenements/'}}})

            elif str(Id) == '30':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Nombre '}}})

                for i in self.STG_projects_pro_list.find({"TITLE":name}, {"DESCRIPTION":1, "_id":0})[0].get("DESCRIPTION") :

                        if 'Periodo' in i:
                            self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":i}})
                            self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"START DATE": i[8:18] }})
                            
                            #Classify start and end date
                            if len(i) > 20 :
                                self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"END DATE": i[21:31] }})

            elif str(Id) == '38':

                #Classify dates and remove it
                for i in self.STG_projects_pro_list.find({"TITLE":name})[0].get("DESCRIPTION"):
                    if 'Project Duration' in i:
                        self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"START DATE": i[17:27] }})
                        self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"END DATE": i[29:39] }})

                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Project Duration'}}})
                
                

            elif str(Id) == '35':

                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['À LA UNE', 'À lire  :', 'A lire  :', 'Contact  ' ]}}})

                prev_str = ''

                for i in self.STG_projects_pro_list.find({"TITLE":name}, {"DESCRIPTION":1, "_id":0})[0].get("DESCRIPTION")  :
                    if i.count(' ') <= 1 :
                        self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":i}})
                         
                        prev_str = prev_str + " " + i
                
                #Insert joined text
                self.STG_projects_pro_list.update({"TITLE":name},{"$addToSet":{"DESCRIPTION": prev_str }})            



            elif str(Id) == '124':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['1', '2' ]}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.nhm.ac.uk/take-part/'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['Get the latest updates from our citizen science team']}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Project Plumage '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Big Seaweed Search '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'UK Whale and Dolphin Strandings '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Earthworm '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Miniature Lives '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'The Microverse Discover '}}}) 
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Decoding Nature Students '}}}) 

            elif str(Id) == '31':      
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['           Mitforschen                   ', \
                '           Blog                   ', '           Citizen Science                   ', '           Netzwerk                   ', \
                '           Veranstaltungen                   ', '                         Anmelden                                 ', \
                '                         Newsletter                   ', '                         Über uns                                 ', \
                '                         EN                                 ', '1', '2', '3', '                       Presse                               ', \
                '                       Impressum                               ', '                       Datenschutz                               ', \
                '                       Disclaimer                               ', '                       Nutzungsbedingungen für Projektinitiator*innen                                '\
                'Toggle Menu', 'Toggle Search', 'Suche', 'sofort losforschen', '4', '5', '6', '7', '8', 'Toggle Menu', 'mit App', 'Aktionszeitraum' ]}}})

                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex": 'innen '}}})
            
            elif str(Id) == '32':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['HOME', 'citizenscience:germany', 'IMPRESSUM'\
                'DATENSCHUTZ','BERICHTE/KOMMENTARE', 'PROJEKTE', 'IDEEN', 'ONLINE-DOSSIER', 'Partner:' ]}}})

                
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'IMPRESSUM'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'DATENSCHUTZ'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Sign up as an Entrepreneur'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Foto oben: Markus Wegner/www.pixelio.de'}}})

            elif str(Id) == '33':
                
                self.STG_projects_pro_list.remove({"TITLE":{"$regex":"No se puede acceder a este sitio web"}})

                #Remove data    
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['FAQ', 'Aktuelle Veranstaltungen' , \
                'TransferschuleAktuelle VeranstaltungenVeranstaltungsarchivTransferbibliothek', 'Veranstaltungsarchiv', 'Transferbibliothek', \
                'Citizen ScienceCS@WWUCS WettbewerbMitforschenNetzwerk', 'CS@WWU', 'CS Wettbewerb', 'Mitforschen', 'Netzwerk', \
                'HomeCitizen Scienceduewelsteene', 'Citizen Scienceduewelsteene', 'duewelsteene', 'Facebook', 'Impressum', 'Datenschutzhinweis', \
                'Website', 'Cookies', 'Arbeitsstelle Forschungstransfer', '48149', 'Münster', '+49 251 83-32221', '+49 251 83-32123', \
                'wissen', 'leben', 'Erfindungsmeldung', 'WWU Technologieangebote / Erfindungen', 'Veranstaltungen', \
                'Gesetzliche Grundlagen', 'Erfindersprechstunde', 'Gründungen', 'Abgeschlossene Projekte', 'MUIMUN', 'Gesetzliche Grundlagen', \
                'Bioinspiration', 'Expedition Münsterland', 'Ideen-Mining', 'Anfahrt und Lageplan', \
                'Trainees & Stipendiaten', 'Wirtschaftsbeirat', 'Transferpreis', 'Jahresberichte', 'Team', 'zur Subnavigation',  \
                'Robert-Koch-Straße 4048149 Münster',  ]}}})

                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'PatenteErfindersprechstundeGesetzliche'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'WissenstransferIdeen'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Die AFOTeamJahresberichteTransferpreisWirtschaftsbeiratTrainees'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Diese Website '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'© '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'zum Inhalt'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'zur Hauptnavigation'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Enabling Innovation'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Innovationslabor'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Außendarstellung der'}}})


            elif str(Id) == '128':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['FOLLOW US', 'Photo credits:' \
                   '×', ' Close ', 'Contact Ed', ' ', 'Follow us' ]}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'©'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'We will never sell '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'By using our site '}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":'Get access to free resources '}}})

                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://earthwatch.org.uk/'}}})

            elif str(Id) == '60':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['Mosquito Alert', 'BioBlitzBcn', 'Líquenes de Barcelona'\
                    'Inici', '»', 'InSPIRES', 'Floodup', 'Red de Observadores Meteorológicos', 'Plant*tes', 'Observadores del Mar', 'Juegos para el Cambio Social'\
                     ]}}})

                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.barcelona.cat/barcelonaciencia/es/'}}})
      
            elif str(Id) == '61':
                #Remove data
                if 'ACTUALIDAD CIENTÍFICA' in name:
                    self.STG_projects_pro_list.remove({"TITLE":name})
                else:
                    self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://fundaciondescubre.es/#'}}})
                    self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['CONTÁCTANOS IR AL SITIO WEB']}}})

            elif str(Id) == '66':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['Ataria - Ciencia Ciudadana', 'Ataria - Ciencia Ciudadana - Programas de Conservación'\
                    'Compartir en Facebook', 'Compartir en Twitter', 'Compartir en Linkedin', 'Enviar correo', 'Centro de Estudios Ambientales', 'Ciencia Ciudadana' \
                    '¿Qué es Ciencia Ciudadana?', '100&CIA', 'Programas de Conservación', 'Programas de Seguimiento', 'Cartografía', 'Banco fotográfico', 'Contacto'\
                    'https://www.twitter.com/vg_ataria(Se abre en una ventana nueva)', 'Enlaces de interés', 'Ataria', 'Anillo Verde', 'Escuchar la página' ]}}})

                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'mailto:'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.vitoria-gasteiz.org/wb021/was/contenidoAction.do?idioma=es&uid='}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://www.vitoria-gasteiz.org/we001/was/we001Action.do?idioma=es'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'https://sedeelectronica.vitoria-gasteiz.org/'}}})
      
            elif str(Id) == '63':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['1', '2', '3' ]}}})


            elif str(Id) == '134':
                #Remove data
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['Get involved', 'Become a collaborator', 'Interested in a PhD at the LRCFS?' \
                    'Where possible, we encourage you to get involved in our work through citizen science', 'Collaborate with us to improve forensic science now and for the future' \
                    'Find out further details about our PhD opportunities' ]}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'/getinvolved/'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'/collaborators/'}}})
                self.STG_projects_pro_list.update({"TITLE":name},{"$pull":{"WEB":{"$regex":'/forensic-science/'}}})


            elif str(Id) == '65':
                #Move and map category

                Url_elem = self.check_data_cleaning.find({"Id":3})[0]
                
                try:
                    #For each webpage stored, classify information and map text
                    for i in self.STG_projects_pro_list.find({"TITLE":name}, {"WEB":1, "_id":0})[0].get("WEB") :                 

                        #Topics, if contins "topic"
                        if 'topic' in i :
                            for item in Url_elem['Topics'] : 
                                #Check if the webpage is in list of topics: CSTrack_check_data_cleaning
                                if item['Url'] == i :
                                    #Remove webpage
                                    self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"WEB":i}})
                                    #Add new descriptor
                                    self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "TOPICS": item['Description']}})

                        #Age group, if contins "audience"
                        elif 'audience' in i :
                            for item in Url_elem['Age group'] : 
                                #Check if the webpage is in list of topics: CSTrack_check_data_cleaning
                                if item['Url'] == i :
                                    #Remove webpage
                                    self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"WEB":i}})
                                    #Add new descriptor
                                    self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "MEMBER AGE": item['Description']}})
                        
                        #Development time, if contins "activity"
                        elif 'activity' in i :
                            for item in Url_elem['Development time'] : 
                                #Check if the webpage is in list of topics: CSTrack_check_data_cleaning
                                if item['Url'] == i :
                                    #Remove webpage
                                    self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"WEB":i}})
                                    #Add new descriptor
                                    self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "DEVELOPMENT TIME": item['Description']}})
                        
                        elif 'phrase' in i :
                            #Remove webpage
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"WEB":i}})
                            #Add new descriptor
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "TOPICS": i.partition('=')[2] }})
                except:
                    pass



                #Remove data
                self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$in":['more', 'Loading map...', 'View map...', 'Then…']}}})
                    #contains
                self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex": 'DESCRIPTION '}}})
                self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex": ' on Twitter'}}})
                self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex": ' on Facebook'}}})
                self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex": ' people are talking about '}}})
                self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex": 'No one is talking about '}}})
                self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex": '1 person is talking about'}}})

                #Tools and materials move to descriptor
                try:
                    for i in self.STG_projects_pro_list.find({"TITLE":name}, {"DESCRIPTION":1, "_id":0})[0].get("DESCRIPTION") :                 
                        
                        if "MATERIALS" in i:
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":"MATERIALS"}}})
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "TOOLS AND MATERIALS": i }})

                        #Social media move to descriptor                   
                        elif "SOCIAL MEDIA" in i:
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":"SOCIAL MEDIA"}}})
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "SOCIAL MEDIA": i }})

                        #Participants profile move to descriptor
                        elif "SPECIAL SKILLS" in i:
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":"SPECIAL SKILLS"}}})
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "PARTICIPANTS PROFILE": i }})

                        #Web move to descriptor
                        elif "WEB" in i:
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":"WEB"}}})
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "WEB": i }})

                        #Activity type move to descriptor
                        elif "TYPE OF ACTIVITY" in i:
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":"TYPE OF ACTIVITY"}}})
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "ACTIVITY TYPE": i }})

                        #Topics move to descriptor
                        elif "TAGS" in i:
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":"TAGS"}}})
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "TOPICS": i }})
                    
                        #Publications to descriptor
                        elif "MEDIA MENTIONS & PUBLICATIONS" in i or "RESOURCES " in i:
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":"MEDIA MENTIONS & PUBLICATIONS"}}})
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "RESOURCES": i }})

                        #Metodology move to descriptor
                        elif "METHODOLOGY" in i:
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":"HOW TO GET STARTED"}}})
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "METHODOLOGY": i }})

                        #Metodology move to descriptor
                        elif " APP " in i:
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$pull":{"DESCRIPTION":{"$regex":" APP "}}})
                            self.STG_projects_pro_list.update_one({"TITLE":name},{"$addToSet":{ "APPS": i }})

                except:
                    pass
                
    def STG_insert_all(self, Id):

        for x in self.collection_proj.find({"Plat Id": str(Id), "Insert date": str(date.today()) }): #, "Insert date": str(date.today()) 

            title = x["TITLE"]

            #Special character ( ) to be removed
            if title.find("("):
                start = title.find("(")
                end = title.find(")")
                if start != -1 and end != -1:
                    title = title[:start-1]

            if self.STG_projects_pro_list.find({'TITLE': {"$regex":title}}).count == 0:
                #If project does not exist, then insert it

                self.STG_projects_pro_list.insert(x)
            
            else:
                #If project exists: Remove and insert again. New data will be explored:
                self.STG_projects_pro_list.remove({'TITLE': {"$regex":title}})
                self.STG_projects_pro_list.insert(x)

    def FIN_insert_all(self, Id):

        for x in self.STG_projects_pro_list.find({"Plat Id": str(Id), "Insert date": str(date.today()) }):#, "Insert date": str(date.today())
             
            title = x["TITLE"]
            
            #Special character ( ) to be removed
            if title.find("("):
                start = title.find("(")
                end = title.find(")")
                if start != -1 and end != -1:
                    title = title[:start-1]
            
            try:
                language = self.language(Id, x["DESCRIPTION"] )        
            except:
                language = str(self.collection_pla.find({"Id":Id})[0].get("Language"))

            if self.CSTrack_projects_descriptors.find({'TITLE': {"$regex":title}}).count() == 0: #Url platform': {"$regex":url}

                #If project does not exist, then insert it
                self.CSTrack_projects_descriptors.insert_one(x)
                self.CSTrack_projects_descriptors.update({'TITLE': {"$regex":title}},{'$set':{'Language':language}})   #Check!!!

            else:

                #If project exists, then check if there is new information
                for i in range(2,len(list(x.values()))):

                    if 'list' in str(type(list(x.values())[i])):
                        #Go through the array and check if the information already exists
                        for j in range(1, len(list(x.values())[i])) :
                            
                            try:
                                #Read all the information of each descriptor (array) and check if exist. If not, insert.
                                self.CSTrack_projects_descriptors.update({'TITLE': {"$regex":title}},{"$addToSet":{str(list(x)[i]): str(list(x.values())[i][j]) }})
                            except:
                                pass


                    else:
 
                        try:

                            if str(list(x)[i]) != 'Insert date':
                                value =  self.CSTrack_projects_descriptors.find({'TITLE': {"$regex":title}})[0].get(str(list(x)[i]))
                                self.CSTrack_projects_descriptors.update({'TITLE': {"$regex":title}},{"$set":{str(list(x)[i]): value }})
                                self.CSTrack_projects_descriptors.update({'TITLE': {"$regex":title}},{"$addToSet":{str(list(x)[i]): str(list(x.values())[i]) }})
                        except:
                            pass
        
                self.CSTrack_projects_descriptors.update({'TITLE': {"$regex":title}},{"$addToSet":{"Date update": "2021-05-14"}})#str(date.today())


    def prueba(self, Id, wp2_id):

        for x in self.STG_projects_pro_list.find({"Plat Id": str(Id), "Insert date": str(date.today()) }): #, "Insert date": str(date.today())

            name = str(list(x.values())[1])
            Url = str(x["Url platform"])

            try:

                self.STG_projects_pro_list.update({'TITLE': {"$regex": name}},{'$set':{'Wp2 Id': str(wp2_id)}})   #Check!!!
            except:
                pass

    def Datacleaning_projects(self, Id2):

        #Clean projects from one platform by Id or all the projects stored
        if Id2:
            project_list = self.collection_pla.find({"Id": int(Id2)}) 
        else:
            project_list = self.collection_pla.find({"Projects load": "Automatic", "Load": "yes"})


        #Loop of list of project to be cleaned
        for x in project_list:
            Id = list(x.values())[1]
            wp2_id = int(self.collection_pla.find({"Id":Id})[0].get("Wp2 Id"))

            #if is informed as to be loaded
            if str(self.collection_pla.find({"Id":Id})[0].get("Load")) == 'yes' :

                #check the number of projects and if it is a correct value. Insert it if all correct
                self.Check_num_projects (Id) 

                #Step to create STG to clean dat
                self.STG_insert_all(Id)

                #Clean data in STG step
                self.Check_descriptors(Id, wp2_id)

                #Insert data
                self.FIN_insert_all(Id)

        #self.collection_proj.remove({"Plat Id": str(Id2)})


if __name__ == "__main__":

    scraper = DatacleaningProjects()
    scraper.Datacleaning_projects('17')