from sqlalchemy import create_engine, MetaData, Table

engine = create_engine('postgresql://b3c@localhost/biomedtown', convert_unicode=True)
metadata = MetaData(bind=engine)
usersTable = Table('user_auth', metadata, autoload=True)
connection = engine.connect()
usersList = connection.execute('select * from user_auth')
#usersList2 =  connection.execute('select * from users')

