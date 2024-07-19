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
    /data/delete    GET     eg. 127.0.0.1:4345/api/data/delete?uuid=365538fb-d952-448a-8a1a-5a4773ffa2f8&timestamp=123567634432

/api/system/doFullAnalysis      GET
    /system/
    /user/verify    POST
'''

import aiosqlite
from flask import Flask, request, jsonify
import pandas as pd
import asyncio
import os

DATABASE = 'database.db'
app = Flask(__name__)

password = "365538fb-d952-448a-8a1a-5a4773ffa2f8"

async def df_write_sqlite(df, db_name, tb_name, w_type):
    async with aiosqlite.connect(db_name) as con:
        await df.to_sql(tb_name, con, if_exists=w_type, index=False, method='multi')
        print("write success.\n")
    return True

async def df_read_sqlite(db_name, tb_name):
    async with aiosqlite.connect(db_name) as con:
        sql_q = f"SELECT * FROM {tb_name}"
        df = pd.read_sql_query(sql_q, con)
    return df

async def initiate_database(db_name):
    # Ensure the database file exists
    if not os.path.exists(db_name):
        open(db_name, 'w').close()

    async with aiosqlite.connect(db_name) as con:
        await con.execute("""
        CREATE TABLE IF NOT EXISTS record (
            timestamp INTEGER, 
            type INTEGER, 
            satisfaction INTEGER, 
            remark TEXT
        )""")
    return True

def verifier(uuid):
    return password == uuid

@app.route('/')
def hello():
    return "Visit /api to use the interface"

@app.route('/api/data/record', methods=['POST'])
async def dataRecord():
    if verifier(request.args.get("uuid")):
        try:
            timestamp = request.form.get('timestamp')
            type = request.form.get('type')
            satisfaction = request.form.get('satisfaction', None)
            remark = request.form.get('remark', None)

            if not timestamp or not type:
                return 'Missing mandatory parameters: timestamp and type are required', 400

            if satisfaction is not None:
                satisfaction = int(satisfaction)
                if satisfaction < 0 or satisfaction > 100:
                    return 'The satisfaction parameter must be between 0 and 100', 400

            async with aiosqlite.connect(DATABASE) as con:
                # Check if the record already exists
                async with con.execute("SELECT 1 FROM record WHERE timestamp = ?", (timestamp,)) as cursor:
                    exists = await cursor.fetchone()

                if exists:
                    return 'Record with this timestamp already exists', 409

                await con.execute("""
                INSERT INTO record (timestamp, type, satisfaction, remark)
                VALUES (?, ?, ?, ?)
                """, (timestamp, int(type), satisfaction, remark))
                await con.commit()

            return 'Record added successfully'
        except ValueError as e:
            return f'Invalid value for timestamp, type, or satisfaction: {e}', 400
        except Exception as e:
            return f'Illegal form: {e}', 500
    else:
        return 'Verification failed', 401
@app.route('/api/data/get/analysisResult', methods=['GET'])
async def analysisResult():
    if verifier(request.args.get("uuid")):
        try:
            record_type = request.args.get('type', None)
            filter_condition = request.args.get('filter', None)

            df = await df_read_sqlite(DATABASE, 'record')

            if record_type is not None:
                df = df[df['type'] == int(record_type)]

            if filter_condition:
                df = df.query(filter_condition)

            result = df.describe().to_dict()
            return jsonify(result)
        except Exception as e:
            return f'Analysis failed: {e}', 500
    else:
        return 'Verification failed', 401


@app.route('/api/data/change', methods=['POST'])
async def dataChange():
    if verifier(request.args.get("uuid")):
        try:
            timestamp = request.form.get('timestamp')
            type = request.form.get('type')
            satisfaction = request.form.get('satisfaction')
            remark = request.form.get('remark')

            if not timestamp:
                return 'Missing mandatory parameter: timestamp is required', 400

            async with aiosqlite.connect(DATABASE) as con:
                # Check if the record exists
                async with con.execute("SELECT 1 FROM record WHERE timestamp = ?", (timestamp,)) as cursor:
                    exists = await cursor.fetchone()

                if not exists:
                    return 'Record not found', 404

                update_fields = []
                update_values = []

                if type is not None:
                    update_fields.append("type = ?")
                    update_values.append(int(type))
                if satisfaction is not None:
                    update_fields.append("satisfaction = ?")
                    update_values.append(int(satisfaction))
                if remark is not None:
                    update_fields.append("remark = ?")
                    update_values.append(remark)

                if not update_fields:
                    return 'No fields provided for update', 400

                update_values.append(timestamp)
                query = f"UPDATE record SET {', '.join(update_fields)} WHERE timestamp = ?"
                await con.execute(query, update_values)
                await con.commit()

            return 'Record updated successfully'
        except ValueError as e:
            return f'Invalid value for type or satisfaction: {e}', 400
        except Exception as e:
            return f'Update failed: {e}', 500
    else:
        return 'Verification failed', 401

@app.route('/api/data/delete', methods=['GET'])
async def dataDelete():
    if verifier(request.args.get("uuid")):
        timestamp = request.args.get('timestamp')

        if not timestamp:
            return 'Missing mandatory parameter: timestamp is required', 400

        try:
            async with aiosqlite.connect(DATABASE) as con:
                # Check if the record exists
                async with con.execute("SELECT 1 FROM record WHERE timestamp = ?", (timestamp,)) as cursor:
                    exists = await cursor.fetchone()

                if not exists:
                    return 'Record not found', 404

                await con.execute("DELETE FROM record WHERE timestamp = ?", (timestamp,))
                await con.commit()

            return 'Record deleted successfully'
        except Exception as e:
            return f'Deletion failed: {e}', 500
    else:
        return 'Verification failed', 401

@app.route('/api/system/doFullAnalysis', methods=['GET'])
async def doFullAnalysis():
    if verifier(request.args.get("uuid")):
        try:
            df = await df_read_sqlite(DATABASE, 'record')
            analysis_result = df.groupby('type').describe().to_dict()
            return jsonify(analysis_result)
        except Exception as e:
            return f'Analysis failed: {e}', 500
    else:
        return 'Verification failed', 401

@app.route('/api/user/verify', methods=['POST'])
def userVerify():
    if verifier(request.form.get("uuid")):
        return 'Verification successful'
    else:
        return 'Verification failed', 401

if __name__ == '__main__':
    asyncio.run(initiate_database(DATABASE))
    app.run(host='0.0.0.0', port=4345, debug=True)