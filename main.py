import requests
import re
import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import dateparser
from Credentials import *


connection_url = URL.create(drivername = 'mssql+pyodbc',query={'odbc_connect':connection_str})
engine = create_engine(connection_url)

url = 'https://api.todoist.com/rest/v2/tasks'

r = requests.get(url,headers=headers)
tasks = r.json()

df = pd.DataFrame(tasks)
mask = df['content'].str.startswith('Update Mileage')
updates = df[mask][['description','id','content']].rename(columns={'description':'FillTime'})

taskIDs = updates.pop('id')

#pattern = 'Update Mileage (.*?) (.*?)$'

#FIXME: exit if no data
milageInfo = updates['content'].str.split(' ',expand=True)

updates['Mileage'], updates['GallonsFilled'] = milageInfo[2], milageInfo[3]
updates['FillTime'] = updates['FillTime'].apply(lambda x:datetime.datetime.strftime(dateparser.parse(x),"%Y-%m-%d %H:%M:%S"))
updates.drop('content',axis=1,inplace=True)

updates.to_sql(name='BuickGas',con=engine,index=False,schema='dbo',if_exists='append')
print('f{len(updates)} rows uploaded')

print('Closing Tasks...')
for taskID in taskIDs:
    r = requests.post(url+f'/{taskID}/close',headers=headers)
print('Done')