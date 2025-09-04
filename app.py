# app.py
from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# connect to database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@0706647669J",
    database="rental_management"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    cursor.execute("SELECT * FROM tenant")
    tenants = cursor.fetchall()
    return render_template('index.html', tenants=tenants)

@app.route('/add_tenant', methods=['POST'])
def add_tenant():
    name = request.form['name']
    number = request.form['number']
    contact = request.form['contact']
    cursor.execute("INSERT INTO tenant (tenant_name, tenant_number, tenant_contact) VALUES (%s, %s, %s)", 
                   (name, number, contact))
    db.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
