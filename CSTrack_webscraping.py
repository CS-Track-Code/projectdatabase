import bs4, requests, pymongo, pprint

from pymongo import MongoClient

#Mongodb connection
conn = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')

#Mongodb database and repository
db = conn.CSTrack
collection = db.projects_pla_list
collection_proj = db.projects_pro_list


#Get list of projects in platform CS spain. 
def getCsPlatformProjects(platformUrl, annexed, check, country):
    res = requests.get(platformUrl)
    #  print(res.raise_for_status) #[200] ok
    soup =bs4.BeautifulSoup(res.text,'html.parser')
    #elems=soup.select('#et-boc > div > div > div.et_pb_section.et_pb_section_1.et_section_regular > div > div > div > div.et_pb_portfolio_items_wrapper.clearfix')
    
    #For all the information in webpage recover 'a' tag information
    for link in soup.find_all('a'): 
        
        try:
            if link.text.strip() != '': #Check if the tag has information
                     
                if check != '': #Check if there is information in the "check" variable
                    #Check if is a valid information for each platform
                    if str(check) in str(link['href']) :    #Check if the information in the "check" variable is in the text retrieve
                        if annexed != '':   #Check if there is information in the "annexed" variable
                            #annexed is used to url that only show the route, not the main page link
                            collection.insert_one({'Url':annexed+link['href'], 'Name': link.text.strip(), 'Country':country})
                        else:
                            collection.insert_one({'Url':link['href'], 'Name': link.text.strip(), 'Country':country})
                else:
                    if annexed != '':
                        #annexed is used to url that only show the route, not the main page link
                        collection.insert_one({'Url':annexed+link['href'], 'Name': link.text.strip(), 'Country':country})
                    else:
                        collection.insert_one({'Url':link['href'], 'Name': link.text.strip(), 'Country':country})          
        except:
            print('uf')
#Get for all the projects the information in tags  
def getInfoProjects(projectUrl):
    res = requests.get(projectUrl)
    #  print(res.raise_for_status) #[200] 
    soup =bs4.BeautifulSoup(res.text,'html.parser')

    #For each tag 'div' recover tittle and description information
    for tag in soup.find_all('div'):
                
        for i in range(len(tag)):   #For each value in the tag
            
            titulo = tag.find_next('h1')    #Tittle tag
            try:    # If Attribute error then do nothing
                if titulo.text.strip() and titulo.text.strip() not in projects[0:] :    #if tittle is informed and is not in project list
                    projects.append('TITULO')   #Add tittle and description for projects list
                    projects.append(titulo.text.strip())
            except AttributeError:
                print('pff') 
            
            descriptivo = tag.find_all('p')      #Description information is in 'p' tag

              
            try:           
                etiqueta = descriptivo[i].find_previous('h3')  #tittle information is in tag 'h3'
                  
                if descriptivo[i].text.strip('\t') not in projects[0:] and etiqueta != None:    #if description is not in list and tittle is not empty
                    projects.append(etiqueta.text.strip())
                    projects.append(descriptivo[i].text.strip('\n'))
                    
                elif descriptivo[i].text.strip('\t') not in projects[0:] :  #if description is not in list
                    projects.append('DATO')
                    projects.append(descriptivo[i].text.strip('\t'))
                    
            except IndexError:
                print('pff')  

#Convert a list as a dictionary
def dictionaryConversion(lst): 

    for i in range(0, len(lst),2):  #For each value in list moving 2 steps for each loop


        if lst[i] not in list(res_dct.keys())  :    #If tittle is not in dictionary (key values)
            res_dct[lst[i]] = lst[i+1]      #Assign description to a tittle: one value each time
        else :                                      #If tittle is in dictionary 
            res_dct[lst[i]] = [str(res_dct[lst[i]]).strip('[]'),str(lst[i+1])]  #Create a list of values (strip separate values from previous list defined)

    return res_dct 

#Populate the database with url projects for each platform
getCsPlatformProjects('https://www.schweiz-forscht.ch/de/citizen-science-projekte/gesellschaft','', '','CHE')
print(collection)

#Loop to read for each project in platform the tags informed
'''for x in collection.find():
    projects = []
    res_dct = {}
    #print(list(x.values())[1])
    getInfoProjects(list(x.values())[1])    #Retrieve all tag informed
    collection_proj.insert_one(dictionaryConversion(projects))  #For the dictionary created from a list, insert each one in database'''

