status = 'local'

# DATABANK
if status == 'local':
    
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = 'senai'
    DB_NAME = 'Rotalks'

elif status == 'production':
    DB_HOST = 'PedroEdRoel.mysql.pythonanywhere-services.com'
    DB_USER = 'PedroEdRoel'
    DB_PASSWORD = 'amongus123'
    DB_NAME = 'PedroEdRoel$Rotalks'

# SECRET KEY

SECRET_KEY = 'blog'

# ADM

MASTER_PASSWORD = 'o1_51@6f%H_-'
ADM_EMAIL = 'pedroroel@gmail.com'