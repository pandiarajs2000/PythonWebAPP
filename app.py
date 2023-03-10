from flask import Flask,render_template,request,redirect,url_for,flash
from flask_mysqldb import MySQL

app = Flask(__name__)

#mysql connection
app.config["MYSQL_HOST"] = 'localhost'
app.config["MYSQL_USER"] = 'pandiaraj'
app.config["MYSQL_PASSWORD"] = 'Pandi@2000'
app.config["MYSQL_DB"] = 'InventoryDB'
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql = MySQL(app)

#home_page
@app.route('/home')
def home_page():
    return render_template('home_page.html')

#product_add page
@app.route('/product_add',methods = ['GET','POST'])
def product_add():
    
    if request.method == "POST":
        
        pro_id = request.form['product_id']
        pro_desc = request.form['product_desc']

        con = mysql.connection.cursor()
        sql = "INSERT INTO products(product_id,product_desc) value(%s,%s)"
        con.execute(sql,[pro_id,pro_desc])
        mysql.connection.commit()
        con.close()
        flash('Product Add Successfully')
        return redirect(url_for('product_add'))
    return render_template('product_add.html')

#product fetch query
@app.route('/product_query')
def product_query():
    con = mysql.connection.cursor()
    sql = "select * from products"
    con.execute(sql)
    result = con.fetchall()
    print(result)
    return render_template('product_add.html',datas = result)

#product update
@app.route("/product_update/<string:product_id>",methods = ['GET','POST'])
def product_update(product_id):
    con = mysql.connection.cursor()
    if request.method == 'POST':
        product_id = request.form['product_id']
        product_desc = request.form['product_desc']
        sql = "update products set product_desc = %s where product_id = %s"
        print(sql)
        con.execute(sql,[product_desc,product_id])
        mysql.connection.commit()
        con.close()
        return redirect(url_for('product_add'))

    con = mysql.connection.cursor()
    sql = "select * from products where product_id = %s"
    con.execute(sql,[product_id])
    result = con.fetchone()
    return render_template('product_update.html',datas = result)

#product delete query
@app.route("/product_delete/<string:product_id>",methods = ['GET','POST'])
def product_delete(product_id):
    con = mysql.connection.cursor()
    sql = "delete from products where product_id = %s"
    con.execute(sql,[product_id])
    mysql.connection.commit()
    con.close()
    return redirect(url_for('product_add'))

#location add
@app.route('/location_page',methods = ['GET','POST'])
def location_page():

    if request.method == "POST":
        
        loc_id = request.form['location_id']
        loc_desc = request.form['location_desc']
        
        con = mysql.connection.cursor()
        sql = "INSERT INTO location(location_id,location_desc) value(%s,%s)"
        #print("coming to location_page &&&&&&&",sql)
        con.execute(sql,[loc_id,loc_desc])
        mysql.connection.commit()
        con.close()
        flash('Location Add Successfully')
        return redirect(url_for('location_page'))
    return render_template('location_add.html')

#location update query
@app.route("/location_update/<string:location_id>",methods = ['GET','POST'])
def location_update(location_id):
    con = mysql.connection.cursor()
    if request.method == 'POST':
        location_id = request.form['location_id']
        location_desc = request.form['location_desc']
        sql = "update location set location_desc = %s where location_id = %s"
        print(sql)
        con.execute(sql,[location_desc,location_id])
        mysql.connection.commit()
        con.close()
        return redirect(url_for('location_page'))

    con = mysql.connection.cursor()
    sql = "select * from location where location_id = %s"
    con.execute(sql,[location_id])
    result = con.fetchone()
    return render_template('location_update.html',datas = result)

#loaction fetch query
@app.route('/location_query')
def location_query():
    con = mysql.connection.cursor()
    sql = "select * from location"
    con.execute(sql)
    result = con.fetchall()
    #print("coming to location_query **********", result)
    return render_template('location_add.html',datas = result)

#location delete query
@app.route("/location_delete/<string:location_id>",methods = ['GET','POST'])
def location_delete(location_id):
    con = mysql.connection.cursor()
    sql = "delete from location where location_id = %s"
    con.execute(sql,[location_id])
    mysql.connection.commit()
    con.close()
    return redirect(url_for('location_page'))


#product move
@app.route('/productmove',methods = ['GET','POST'])
def productmove():
    existing_qty=0
    if request.method == "POST":
        pro_id = request.form['product_id']
        date_time = request.form['date']
        from_loc = request.form['from_location']
        to_loc = request.form['to_location']
        qty = request.form['qty']
        
        print("print => ",pro_id,date_time,from_loc,to_loc,qty)
        print("to_location",len(to_loc))
        if len(to_loc) > 1:
            #print(to_loc)
            con = mysql.connection.cursor()
            existing_qty_sql = "select max(qty) as qty from productmovements"
            
            con.execute(existing_qty_sql)
            existing_qty_dic = con.fetchone()
            existing_qty=existing_qty_dic.get('qty')
            #mysql.connection.commit()
            con.close()
            print("quantity => ",existing_qty,from_loc)
            if(int(existing_qty) >= int(qty)):
                print("existing quantity", existing_qty)
                print("existing quantity type", type(existing_qty))
                print(" quantity type", type(qty))
                con = mysql.connection.cursor()
                #update
                sql_update = "update productmovements set qty = %s where product_id = %s and from_location = %s"
                print("update query", sql_update, "int(existing_qty)-int(qty)", int(existing_qty)-int(qty))
                con.execute(sql_update,[int(existing_qty)-int(qty),pro_id,from_loc])
                #insert
                sql_insert = "insert into productmovements (product_id,date_time,from_location,to_location,qty) value(%s,%s,%s,%s,%s)"
                con.execute(sql_insert,[pro_id,date_time,from_loc,to_loc,qty])
                print("sql insert",sql_insert)
                mysql.connection.commit()
                con.close()
            
            elif (existing_qty <= qty):
                #warning message
                #update qty as 0
                sql_update = "update productmovements set qty = 0 where movement_id = %s"
                #insert
                sql_insert = "insert into productmovements (product_id,date_time,from_location,to_location,existing_quantity - qty) value(%s,%s,%s,%s,%s)"
                con.execute(sql_update[pro_id,date_time,from_loc,to_loc,qty],sql_insert[pro_id,date_time,from_loc,to_loc,qty])
                mysql.connection.commit()
                con.close()
        else:
            con = mysql.connection.cursor()
            sql = "INSERT INTO productmovements(product_id,date_time,from_location,to_location,qty) value(%s,%s,%s,%s,%s)"
            print(sql)
            con.execute(sql,[pro_id,date_time,from_loc,to_loc,qty])
            mysql.connection.commit()
            con.close()
        flash("Product Moved Successfully")
        return redirect(url_for('productmove'))
    return render_template('product_movement.html')

#product_move_update query
@app.route("/product_move_update/<string:movement_id>",methods = ['GET','POST'])
def product_move_update(movement_id):
    con = mysql.connection.cursor()
    print("movementid ->",movement_id)
    #print("Date =>",date_time)
    if request.method == 'POST':
        product_id = request.form['product_id']
        date_time = request.form['date_time']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        qty = request.form['qty']
        print("quantity",qty)

        sql = "update productmovements set product_id = %s, date_time = %s, from_location = %s, to_location = %s, qty = %s where movement_id = %s"
        con.execute(sql,[product_id,date_time,from_location,to_location,qty,movement_id])
        mysql.connection.commit()
        con.close()
        return redirect(url_for('productmove'))

    con = mysql.connection.cursor()
    sql = "select * from productmovements where movement_id = %s"
    con.execute(sql,[movement_id])
    result = con.fetchone()
    return render_template('productmove_update.html',datas = result)


#product_move_delete query
@app.route('/product_move_delete/<string:product_id>',methods = ['GET','POST'])
def product_move_delete(product_id):
    con = mysql.connection.cursor()
    sql = "delete from productmovements where product_id = %s"
    con.execute(sql,[product_id])
    mysql.connection.commit()
    con.close()
    return redirect(url_for('productmove'))


#product_move_fetch query
@app.route('/product_move_fetch_query')
def product_move_fetch_query():
    con = mysql.connection.cursor()
    sql = "select * from productmovements"
    con.execute(sql)
    result = con.fetchall()
    #print(result)
    return render_template('product_movement.html',datas = result)



#report_fetch query
@app.route('/report')
def report_page():
    con = mysql.connection.cursor()
    sql = "select product_id, from_location as location, max(qty) as qty from productmovements where length(to_location)=0 group by from_location, product_id order by from_location asc;"
    
    con.execute(sql)
    result = con.fetchall()
    print(type(result))

    sql = "select product_id, to_location as location, max(qty) as qty from productmovements where length(to_location)>1 group by to_location, product_id order by to_location asc;" 
    con.execute(sql)
    result1 = con.fetchall()

    print(result+ result1)


    return render_template('report.html',datas = result+result1)



if __name__  == "__main__":
    app.secret_key = "pandi"
    app.run(debug = True)