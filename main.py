"""ก๋วยเตี๋ยวร่มลื่น"""
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import json
import random
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')
#print('>>>', DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)

app = Flask(__name__)
connection = mysql.connector.connect(
    host=DB_HOST,
    port=3306,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_DATABASE
)
curs = connection.cursor()
pick = ''

@app.route('/')
def firstpage():
    return render_template('firstpage.html')

@app.route('/table')
def table():
    return render_template('table.html')

@app.route('/name')
def name():
    return render_template('takehome.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        random_id = random.randrange(0, 1000000)
        print('=====================')
        print(name, random_id)
        print('=====================')
        sql = 'INSERT INTO users (id, name, menus) VALUES (%s, %s, %s)'
        curs.execute(sql, (random_id, name, '[]'))
        connection.commit()
    return render_template('home.html', myname=name)

@app.route('/menu', methods=['GET', 'POST'])
def menu_list():
    curs.execute('SELECT * FROM noodle')
    row = curs.fetchall()
    all_total_price = 0
    #print(*row, sep='\n')
    if request.method == 'POST':
        curs.execute('SELECT type FROM options')
        options = [i[0] for i in curs.fetchall()]
        all_picked_options = []
        for group in options:
            all_picked_options += request.form.getlist(group)
        menu_pick = pick
        total_price = 0
        sql = "SELECT price FROM prices WHERE name = %s"
        curs.execute(sql, (menu_pick, ))
        main_price = curs.fetchall()[0][0]
        print(main_price)
        total_price += int(main_price)
        for option in all_picked_options:
            sql = "SELECT price FROM prices WHERE name = %s"
            curs.execute(sql, (option, ))
            each_price = curs.fetchall()[0][0]
            print('>>>', each_price)
            total_price += int(each_price)
        print(total_price)
        print(all_picked_options)
        curs.execute('SELECT menus, price FROM users WHERE id=0')
        yea = curs.fetchall()
        #print('>>>', yea)
        orders = json.loads(yea[0][0].replace("'", '"'))
        price = int(yea[0][1])
        #print('>>>', orders)
        orders += [{pick : [all_picked_options, total_price]}]
        all_total_price += total_price
        all_total_price += price
        #print('>>>', orders)
        orders = str(orders)
        sql = "UPDATE users SET menus= %s, price = %s WHERE id = %s"
        curs.execute(sql, (orders, all_total_price, 0))
        connection.commit()
    return render_template('menu.html', datas=row)

@app.route('/option', methods=['GET', 'POST'])
def option_list():
    curs.execute('SELECT * FROM options')
    row = curs.fetchall()
    #print(*row, sep='\n')
    curs.execute('SELECT adding FROM options')
    each_option = curs.fetchall()
    #print(*each_option, sep='\n')
    each_option = [json.loads(item[0]) for item in each_option]
    print(each_option)
    if request.method == 'POST':
        global pick
        pick = request.form['pick']
    return render_template('noodle.html', pick=pick, datas=row, each_option=each_option)

@app.route('/ordersummary', methods=['GET', 'POST'])
def order_summary():
    curs.execute('SELECT menus, price FROM users WHERE id = 0')
    user_get = curs.fetchall()
    print('>>>>>>>>>>>>>>', user_get)
    orders = json.loads(user_get[0][0].replace("'", '"'))
    print('>>>>>>>>>>>>>>', orders)
    price = int(user_get[0][1])
    print(price)
    if request.method == 'GET':
        mai = request.form['eiei']
        print(mai)
        #del orders[delete]
        #price -= list(orders[orders.index[delete]].values())[0][-1]
        print('**************', orders)
    return render_template('ordersummary.html', datas=orders, price=price)

@app.route('/complete')
def complete():
    return render_template('complete.html')

if __name__ == '__main__':
    app.run(debug=True)