from environs import Env

env = Env()
env.read_env()

USER = env("USER")
PASSWORD = env("PASSWORD")
HOST = env("HOST")
CONNECTIONSTR = env("CONNECTIONSTR")
PORTDEV = env("PORTDEV")
PORTPROD = env("PORTPROD")
