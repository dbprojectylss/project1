# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "ss5620"
DB_PASSWORD = "2lFJrIBi3r"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass




@app.route('/login_to', methods=['POST'])
def login_to():
    usertype = request.form['usertype']
    if usertype == 'customer':
        global cid
        cid = request.form['loginid']
        cursor = g.conn.execute("SELECT pid, sum(storage) FROM manage GROUP BY pid ORDER BY pid")
        results = []
        results.append("Pid, Storage:")
        for result in cursor:
            results.append(result)
        cursor.close()
    
        context = dict(data=results)
        return render_template("product.html", **context)
    else:
        global sid
        sid = request.form['loginid']
        cursor = g.conn.execute('SELECT pid, storage FROM manage WHERE sid=%s ORDER BY pid', int(sid))
        results = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for result in cursor:
            if result!='':
                results[result[0]-10001]=result[1]
        cursor.close()
        context = dict(data=results)
        
        return render_template("seller.html", **context)
  
@app.route('/register_to', methods=['POST'])
def register_to():
    usertype = request.form['registertype']
    if usertype == 'customer':
        cid = request.form['registerid']
        name = request.form['registername']
        cursor = g.conn.execute('INSERT INTO customer(cid, name) VALUES (%s, %s)', (cid, name))
        cursor = g.conn.execute('INSERT INTO modify_cart(cart_id, name, cid) VALUES (%s, %s, %s)', (int(cid)+100, name, cid))
        cursor = g.conn.execute("SELECT pid, sum(storage) FROM manage GROUP BY pid ORDER BY pid")
        results = []
        results.append("Pid, Storage:")
        for result in cursor:
            results.append(result)
        cursor.close()
    
        context = dict(data=results)
        return render_template("log_in.html", **context)
    else:
        sid = request.form['registerid']
        name = request.form['registername']
        cursor = g.conn.execute('INSERT INTO seller(sid, name) VALUES (%s, %s)', (sid, name))
        cursor = g.conn.execute('SELECT pid, storage FROM manage WHERE sid=%s ORDER BY pid', int(sid))
        results = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for result in cursor:
            if result!='':
                results[result[0]-10001]=result[1]
        cursor.close()
        context = dict(data=results)
        
        return render_template("log_in.html", **context)

@app.route('/product', methods=['GET', 'POST'])
def ProductList():
    cursor = g.conn.execute("SELECT pid, sum(storage) FROM manage GROUP BY pid ORDER BY pid")
    results = []
    results.append("Pid, Storage:")
    for result in cursor:
        results.append(result)
    cursor.close()

    context = dict(data=results)
    return render_template("product.html", **context)
        

@app.route('/ModifyCart', methods=['POST'])
def ModifyCart():
#    cid = request.form['customerid']
    qty=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    qty[0]=request.form['qty1']
    qty[1]=request.form['qty2']
    qty[2]=request.form['qty3']
    qty[3]=request.form['qty4']
    qty[4]=request.form['qty5']
    qty[5]=request.form['qty6']
    qty[6]=request.form['qty7']
    qty[7]=request.form['qty8']
    qty[8]=request.form['qty9']
    qty[9]=request.form['qty10']
    qty[10]=request.form['qty11']
    qty[11]=request.form['qty12']
    qty[12]=request.form['qty13']
    qty[13]=request.form['qty14']
    qty[14]=request.form['qty15']
    
    for i in range(15):
        if qty[i]!='':
            cursor = g.conn.execute("SELECT qty FROM represent WHERE cid=%s and pid=%s", (cid, 10001+i))
            old_val = cursor.fetchone()
            if not old_val:
                engine.execute("""INSERT INTO represent(pid, cid, qty, cart_id) VALUES (%s, %s, %s, %s)""", (10001+i, cid, int(qty[i]), 100+int(cid)))
            elif (int(old_val[0])+int(qty[i])) <= 0:
                g.conn.execute('DELETE FROM represent WHERE cid=%s and pid=%s', (cid, 10001+i))
            else:
                g.conn.execute('UPDATE represent SET qty=%s WHERE cid=%s and pid=%s', (int(old_val[0])+int(qty[i]), cid, 10001+i))
    
    cursor = g.conn.execute("SELECT pid, sum(storage) FROM manage GROUP BY pid ORDER BY pid")
    results = []
    results.append("Pid, Storage:")
    for result in cursor:
        results.append(result)
    cursor.close()
    
    context = dict(data=results)
    return render_template("product.html", **context)

@app.route('/gotocart', methods=['POST'])
def gotocart():
#    cid = request.form['customerid']
    cursor = g.conn.execute("""WITH count_pid(pid, count) AS 
                                          (SELECT pid, sum(qty) 
                                          FROM represent GROUP BY pid),
                                      promote_discount2(pid) AS
                                          (SELECT C.pid
                                          FROM count_pid as C
                                          WHERE C.count >= 100)
                                      SELECT R.pid, P.name, P.price, R.qty, R.pid in (SELECT pid FROM promote_discount2) AS Discount, (1-0.2*CAST(R.pid in (SELECT pid FROM promote_discount2) AS INT))*P.price AS discounted_price 
                                          FROM represent R, product P
                                          WHERE cid=%s and P.pid=R.pid
                                          ORDER BY pid""", int(cid))

    results = []
    results.append('Pid, Name, Price, Qty, Discount, Adjusted price:')
    for result in cursor:
        results.append(result)
    cursor.close()
      
    context = dict(data=results)
    return render_template("cart.html", **context)

@app.route('/seller', methods=['POST'])
def StorageList():
#    sid = request.form['sellerid']
    cursor = g.conn.execute('SELECT pid, storage FROM manage WHERE sid=%s ORDER BY pid', int(sid))
    results = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for result in cursor:
        if result!='':
            results[result[0]-10001]=result[1]
    cursor.close()
    context = dict(data=results)
    return render_template("seller.html", **context)
  
  

@app.route('/ModifyStore', methods=['POST'])
def ModifyStore():
#    sid = int(request.form['sellerid'])
    qty=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    qty[0]=request.form['qty1']
    qty[1]=request.form['qty2']
    qty[2]=request.form['qty3']
    qty[3]=request.form['qty4']
    qty[4]=request.form['qty5']
    qty[5]=request.form['qty6']
    qty[6]=request.form['qty7']
    qty[7]=request.form['qty8']
    qty[8]=request.form['qty9']
    qty[9]=request.form['qty10']
    qty[10]=request.form['qty11']
    qty[11]=request.form['qty12']
    qty[12]=request.form['qty13']
    qty[13]=request.form['qty14']
    qty[14]=request.form['qty15']

    for i in range(15):
        if qty[i]!='':
            cursor = g.conn.execute("SELECT storage FROM manage WHERE sid=%s and pid=%s", (sid, 10001+i))
            old_val = cursor.fetchone()
            if old_val==None:
                g.conn.execute('INSERT INTO manage VALUES (%s, %s, %s)', (sid, 10001+i, int(qty[i])))
#                cursor = g.conn.execute("SELECT storage FROM manage WHERE sid=%s and pid=%s", (sid, 10001))
#                value = cursor.fetchone()
#                g.conn.execute('UPDATE manage SET storage=%s WHERE sid=%s and pid=%s', (int(value[0])+1, sid, 10001))
            elif (int(old_val[0])+int(qty[i])) <= 0:
                g.conn.execute('DELETE FROM manage WHERE sid=%s and pid=%s', (sid, 10001+i))
            else:
                g.conn.execute('UPDATE manage SET storage=%s WHERE sid=%s and pid=%s', (int(old_val[0])+int(qty[i]), sid, 10001+i))      

    cursor.close()
  
    cursor = g.conn.execute('SELECT pid, storage FROM manage WHERE sid=%s ORDER BY pid', int(sid))
    results = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for result in cursor:
        if result!='':
            results[result[0]-10001]=result[1]
    cursor.close()
    context = dict(data=results)
    return render_template("seller.html", **context)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    return render_template("manage.html")

@app.route('/manageoptions', methods=['POST'])
def manageoptions():
    option = request.form['option']
    results = []

    if option == 'customers':
        cursor = g.conn.execute("SELECT * FROM customer")
        results.append("Customer ID, Name:")
    elif option == 'sellers':
        cursor = g.conn.execute("SELECT * FROM seller")
        results.append("Seller ID, Name:")
    elif option == 'products':
        cursor = g.conn.execute("SELECT * FROM product")
        results.append("Product ID, Name, Price, Category")
    else:
        cursor = g.conn.execute("""WITH count_pid(pid, count) AS 
                                (SELECT pid, sum(qty) 
                                FROM represent GROUP BY pid) 
                               SELECT (M.sid+10000) as did, M.sid, C.pid, 0.8 as amount 
                               FROM count_pid as C, manage as M 
                               WHERE M.pid=C.pid and C.count >= 100""")
        results.append("Discount ID, Seller ID, Product ID, Discount amount:")

    for result in cursor:
        results.append(result)
    cursor.close()

    context = dict(data=results)
    return render_template("manage.html", **context)

@app.route('/')
def loginpage():
    return render_template('log_in.html')

#def index():
#  """
#  request is a special object that Flask provides to access web request information:
#  request.method:   "GET" or "POST"
#  request.form:     if the browser submitted a form, this contains the data in the form
#  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
#  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
#  """
#
#  # DEBUG: this is debugging code to see what request looks like
#  print request.args
#
#
#  #
#  # example of a database query
#  #
#  cursor = g.conn.execute("SELECT name FROM test")
#  names = []
#  for result in cursor:
#    names.append(result['name'])  # can also be accessed using result[0]
#  cursor.close()
#
#  context = dict(data = names)
#
#  return render_template("index.html", **context)

@app.route('/another')
def another():
  return render_template("anotherfile.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print name
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  g.conn.execute(text(cmd), name1 = name, name2 = name);
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()