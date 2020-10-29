
def connection():
        #User
        user = 'root'
        #Password
        password = 'g9k.LS00-1!JbzA8..'
        #host
        host = 'internal-docker.sb.upf.edu'
        #connection string
        connection_str = '/?readPreference=primary&appname=MongoDB%20Compass&ssl=false'
        #port
        port = '8336' #8327 = prod
        
        #LOCALHOST
        #conn = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false') #localhost
        #PROD
        #self.conn = MongoClient('mongodb://root:g9k.LS00-1!JbzA8..@internal-docker.sb.upf.edu:8327/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')
        #TEST
        #conn = MongoClient('mongodb://root:g9k.LS00-1!JbzA8..@internal-docker.sb.upf.edu:8336/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')

        connection =  'mongodb://' + user + ':' + password + '@' + host + ':' + port + connection_str
        return connection

