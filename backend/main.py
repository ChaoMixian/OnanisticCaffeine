'''
API设计
/api/data/record     POST

args            eg
timestamp       1720524475
type            0(Failed)|1(Success)
satisfaction    None|0-100
remark          None|备注

    /data/get/      GET
            /analysisResult?type={}&filter={}
    /data/change    POST
    /data/delete    GET

/api/system/doFullAnalysis      GET
    /system/
    /user/verify    POST
'''
import sqlite3
from flask import Flask, request, g
import pandas as pd
import time
import asyncio

DATABASE = 'database.db'
# con = sqlite3.connect('database.db')
app = Flask(__name__)

password = "365538fb-d952-448a-8a1a-5a4773ffa2f8"

def df_write_sqlite(df, db_name, tb_name, w_type):
    con = sqlite3.connect(db_name)
    df.to_sql(tb_name, con, if_exists=w_type)
    con.close()
    print("write success.")
    return True
    
def df_read_sqlite(db_name, tb_name):
    con = sqlite3.connect(db_name)
    sql_q = "SELECT * FROM {}".format(tb_name)
    df = pd.read_sql_query(sql_q, con)
    con.close()
    return df

def initiate_database(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute("CREATE TABLE record(timestamp, type, satisfaction, remark")
    con.close()
    return True

def write_sqlite(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    con.close()
    return True

def verifier(uuid):
    if (password == uuid):
        return True
    else:
        return False

def test():
    time.slepp(10)
    print("Done!")

async def async_function():
    await asyncio.sleep(3)
    return "Hello, Flask and asyncio!\n"



@app.route('/')
def hello():
    return "visit /api to use the interface"

@app.route('/api/data/record', methods=['GET', 'POST'])
async def dataRecord():
    if verifier(request.args.get("uuid")):
        if request.method == 'POST':
            try:
                timestamp = request.form['timestamp']
                type = request.form['type']
                satisfaction = request.form['satisfaction']
                remark = request.form['remark']
                # 异步实现DB写入
                # await asyncio.sleep(5)
                # return 'Process Done'
                # result = await async_function()
                return await async_function()
            except:
                return 'illegal forms'
        else:
            return 'illegal method'
    else:
        return 'verification failed'


if (__name__=='__main__'):
    app.run(host = '0.0.0.0', port = 4345, debug=True)