from flask import Flask,render_template,url_for,request,jsonify
from dotenv import load_dotenv
import csv , json, os
import psycopg2

app = Flask(__name__)

#database thingssssss
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save",methods=['POST'])
def save():

    if request.method == 'POST':
        data = request.json
        processed = {'processed':data}

        csv_data = []
        for item in data:
            csv_data.append(item.values()) 

        with open('fileSavetyest.csv','w',newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data[0].keys())
            writer.writerows(csv_data)

        app.logger.info(processed)
        return jsonify(processed)
    

@app.route("/tableview",methods=['GET'])
def tableView():
    #get the data from the csv 
    data = list()

    with open('fileSavetyest.csv','r',newline='') as file:
        reader = csv.DictReader(file)
        
        app.logger.info("\nJSON :::")
        app.logger.info(json.dumps(reader.fieldnames))
        data = list(reader)
        # for row in reader:
        #     app.logger.info("INFO ::::\n")
        #     app.logger.info(row['fields'])
            
            # data[f'table_'+row['name']] = row['name']
            # data[f''+row['name']+'_fields'] = row['fields']

    if data:                
        app.logger.info("DATA INFO\n")
        app.logger.info(data)

        return render_template('saved.html',saved_tables = data)
    else:
        return render_template('saved.html')


    # return render_template("saved.html")

#testing the db conncetion 
@app.route("/testing")
def testingDB():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM  db_tables")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("testdb.html",info=rows)

@app.route("/quizzes")
def quizzesLanding():
    return render_template('quizzesLanding.html')

@app.route("/builder")
def tabelBulder():
    return render_template('tableBuilder.html')

@app.route("/textBuilder")
def textBuilder():
    return render_template('textBuilder.html')

##for render to run 
if __name__ == "__main__":
    app.run()
    