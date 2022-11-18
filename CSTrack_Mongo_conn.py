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
        port = config.PORTDEV
        port_prod = config.PORTPROD

        connection =  'mongodb://' + user + ':' + password + '@' + host + ':' + port_prod + connection_str
        return connection