import CSTrack_connection_config  as config

def connection():
        #User
        user = config.USER
        #Password
        password = config.PASSWORD
        #host
        host = config.HOST
        #connection string
        connection_str = config.CONNECTIONSTR
        #port
        port = config.PORTDEV #8327 = prod
        port_prod = config.PORTPROD
        
        #LOCALHOST
        #conn = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false') #localhost
        #PROD
        #self.conn = MongoClient('mongodb://root:g9k.LS00-1!JbzA8..@internal-docker.sb.upf.edu:8327/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')
        #TEST
        #conn = MongoClient('mongodb://root:g9k.LS00-1!JbzA8..@internal-docker.sb.upf.edu:8336/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')

        connection =  'mongodb://' + user + ':' + password + '@' + host + ':' + port + connection_str
        return connection

