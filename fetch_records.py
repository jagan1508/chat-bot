import mysql.connector
import pandas as pd

hostname='localhost'
username='root'
password='jagan2911'
database='jagandb'
table_name='employee'

def convert_to_csv():
    query=f"select * from {table_name}"
    df=pd.read_sql(query,con=connection)
    print(df)
    df.to_csv(f"{table_name}.csv", index=False)
    print("CSV File has been created successfully") 
try:
    connection = mysql.connector.connect(host=hostname, user=username, password=password, database=database)
    cursor=connection.cursor()
    """query=f"select * from {table_name}"  /* Use this to get record in the form of list of tuples
    cursor.execute(query)
    data=cursor.fetchall()"""
    convert_to_csv()
except Exception as e:
    print(f"Error fetching data: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
