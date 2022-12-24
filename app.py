from MySQLdb import MySQLError
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import logging
import sys
app = Flask(__name__)

# mysql connection
app.config["MYSQL_HOST"] = 'localhost'
app.config["MYSQL_USER"] = 'pandiaraj'
app.config["MYSQL_PASSWORD"] = 'Pandi@2000'
app.config["MYSQL_DB"] = 'InventoryDB'
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

logging.basicConfig(
    filename='log/InventoryWebApp.log',
    encoding='utf-8',
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


# home_page
@app.route('/home')
def home_page():
    logger.debug('This is a debug message')
    return render_template('home_page.html')

# product_add page
@app.route('/product_add', methods=['GET', 'POST'])
def product_add():
    message = ''
    logger.info("** inside product add method")
    if request.method == "POST":
        try:
            pro_id = request.form['product_id']
            pro_desc = request.form['product_desc']

            con = mysql.connection.cursor()
            sql = "INSERT INTO products(product_id,product_desc) value (%s,%s)"
            con.execute(sql, [pro_id, pro_desc])
            mysql.connection.commit()
            logger.debug(f"%s Record inserted successfully into product table", con.rowcount)
            if(con.rowcount == 1):
                message = f"The product '{pro_id}' is added successfully. You can now add product stock/movements for '{pro_id}'"
                flash(message, category="message")
            return redirect(url_for('product_add'))
        except MySQLError as ex:
            if("Duplicate" in ex.args[1]):
                message = f"The product {pro_id} is exists already. You cannot add an existing product again.."
                logger.error(f"product_add() Database exception Occurred: %s", ex.args[1])
                flash(message, category="error")
            else:
                flash(ex.args[1], category="error")
                logger.error(f"product_add() Database exception Occurred: %s", ex.args[1])
            return render_template('product_add.html')
        finally:
            con.close()
    return render_template('product_add.html')

# product fetch query
@app.route('/product_query')
def product_query():
    try:
        con = mysql.connection.cursor()
        sql = "select * from products"
        con.execute(sql)
        result = con.fetchall()
        logger.debug(f"Total no.of Products avilable is %s",con.rowcount)
    except MySQLError as ex:
        logger.error(f"product_query() Database exception Occurred: %s", ex.args[1])
    return render_template('product_add.html', datas=result)


# product_view_query
@app.route('/product_update_view')
def product_update_view():
    try:
        con = mysql.connection.cursor()
        sql = "select * from products"
        con.execute(sql)
        res = con.fetchall()
        logger.debug(f"Total no.of products available is %s", con.rowcount)
    except MySQLError as ex:
        logger.error(f"product_query() Database exception Occurred: %s", ex.args[1])
    return render_template('product_add_update.html', datas=res)

# product_update
@app.route("/product_addData_update/<string:product_id>", methods=['GET', 'POST'])
def product_addData_update(product_id):
    con = mysql.connection.cursor()
    message = ""
    if request.method == 'POST':
        product_id = request.form['product_id']
        product_desc = request.form['product_desc']
        try:
            sql = "update products set product_desc = %s where product_id = %s"
            con.execute(sql, [product_desc, product_id])
            logger.debug(f"product_addData_update() update query is: %s %s %s",sql, product_desc, product_id)
            mysql.connection.commit()
            if(con.rowcount == 1):
                message = f"Product '{product_id}' updated successfully.."
                logger.debug(f"product_addData_update() Product '%s' updated successfully", product_id)
                flash(message, category="message")

        except MySQLError as ex:
            logger.error(f"product_addData_update() Database exception Occurred: %s", ex.args[1])
        finally:
            con.close()
        return redirect(url_for('product_update_view'))

    con = mysql.connection.cursor()
    sql = "select * from products where product_id = %s"
    con.execute(sql, [product_id])
    result = con.fetchone()
    return render_template('product_update.html', datas=result)

#product_delete_view_query
@app.route('/product_delete_view')
def product_delete_view():
    try:
        con = mysql.connection.cursor()
        sql = "select * from products"
        con.execute(sql)
        res = con.fetchall()
        logger.debug(f"Total no.of products available is %s", con.rowcount)
    except MySQLError as ex:
        logger.error(f"product_query() Database Exception occured: %s",ex.args[1])
    finally:
        con.close()
    return render_template('product_add_delete.html', datas=res)

# product delete query
@app.route('/product_add_data_delete/<string:product_id>', methods=['GET', 'POST'])
def product_add_data_delete(product_id):
    message = ""
    try:
        con = mysql.connection.cursor()
        sql = "delete from products where product_id = %s"
        con.execute(sql, [product_id])
        mysql.connection.commit()
        if(con.rowcount == 1):
            message = f"This Product '{product_id}' is Deleted.."
            logger.debug(f"product_add_data_delete() %s", message)
            flash(message, category="message")
        return redirect(url_for('product_delete_view'))
    except MySQLError as ex:
        if("Duplicate" in ex.args[1]):
            message = f"This Product '{product_id}' is already exists..."
            logger.error(f"product_add_data_delete() Exception: %s", ex.args[1])
            flash(message, category="error")
        elif("foreign key constraint fails" in ex.args[1]):
            message = f"This Product '{product_id}' is having a warehouse entry, So it cannot be deleted. If you still wanted to delete, please delete the product movement data first.."
            logger.error(f"product_add_data_delete() Exception: %s", ex.args[1])
            flash(message, category="error")
        else:
            logger.error(f"product_add_data_delete() Exception: ", ex.args[1])
            flash(ex.args[1], category="error")
    finally:
        con.close()
    return redirect(url_for('product_delete_view'))

# location add
@app.route('/location_page', methods=['GET', 'POST'])
def location_page():
    message = ""
    if request.method == "POST":
        try:
            loc_id = request.form['location_id']
            loc_desc = request.form['location_desc']

            con = mysql.connection.cursor()
            sql = "INSERT INTO location(location_id,location_desc) value(%s,%s)"
            con.execute(sql, [loc_id, loc_desc])
            mysql.connection.commit()
            if(con.rowcount == 1):
                message = f"The location '{loc_id}' is added successfully. You can now add location stock/movements for '{loc_id}'"
                logger.debug(f"location_page() %s", message)
                flash(message, category="message")
            return redirect(url_for('location_page'))
        except MySQLError as ex:
            if("Duplicate" in ex.args[1]):
                message = f"The location {loc_id} is exists already. You cannot add an existing location again.."
                logger.error(f"location_page() Exception: %s", ex.args[1])
                flash(message, category="error")
            else:
                flash(ex.args[1], category="error")
                logger.error(f"location_page() Exception: %s", ex.args[1])
            return render_template('location_add.html')
        finally:
            con.close()
    return render_template('location_add.html')

# loaction fetch query
@app.route('/location_add_update')
def location_add_update():
    try:
        con = mysql.connection.cursor()
        sql = "select * from location"
        con.execute(sql)
        result = con.fetchall()
        logger.debug(f"Total no.of locations available is %s", con.rowcount)
    except MySQLError as ex:
        logger.error(f"product_query() Database exception Occurred: %s", ex.args[1])
    finally:
        con.close()
    return render_template('location_add_update.html', datas=result)

# location update  query
@app.route("/location_update/<string:location_id>", methods=['GET', 'POST'])
def location_update(location_id):
    con = mysql.connection.cursor()
    message = ""
    if request.method == 'POST':
        location_id = request.form['location_id']
        location_desc = request.form['location_desc']
        try:
            sql = "update location set location_desc = %s where location_id = %s"
            logger.debug(f"location_update() update query is: %s %s %s",sql, location_id, location_desc)
            con.execute(sql, [location_desc, location_id])
            mysql.connection.commit()
            if(con.rowcount == 1):
                message = f"'{location_id}' Location updated successfully.."
                logger.debug(f"location_update() %s", message)
                flash(message, category="message")
        except MySQLError as ex:
            logger.debug(f"location_update() Database exception Occurred: %s", ex.args[1])
        finally:
            con.close()
        return redirect(url_for('location_add_update'))

    con = mysql.connection.cursor()
    sql = "select * from location where location_id = %s"
    con.execute(sql, [location_id])
    result = con.fetchone()
    return render_template('location_update.html', datas=result)

# loaction view query for delete operation
@app.route('/location_add_delete_query')
def location_add_delete_query():
    try:
        con = mysql.connection.cursor()
        sql = "select * from location"
        con.execute(sql)
        result = con.fetchall()
        logger.debug(f"Total no.of Location available is %s",con.rowcount)
    except MySQLError as ex:
        logger.error(f"location_data_view() Database Exception Occured %s",ex.args[1])
    finally:
        con.close()
    return render_template('location_delete_query.html', datas=result)

# location delete query
@app.route("/location_delete/<string:location_id>", methods=['GET', 'POST'])
def location_delete(location_id):
    message = ""
    try:
        con = mysql.connection.cursor()
        sql = "delete from location where location_id = %s"
        con.execute(sql, [location_id])
        mysql.connection.commit()
        if(con.rowcount == 1):
            message = f"The Location '{location_id}' is deleted"
            logger.debug(f"location_delete() %s", message)
            flash(message, category="message")
    except MySQLError as ex:
        if("Duplicate" in ex.args[1]):
            message = f"This location '{location_id}' is already exists..."
            logger.error(f"location_delete() Exception is: %s", ex.args[1])
            flash(message, category="error")
        elif("foreign key constraint fails" in ex.args[1]):
            message = f"This location '{location_id}' is having a warehouse entry, So it cannot be deleted. If you still wanted to delete, please delete the product movement data first.."
            logger.error(f"location_delete() Exception is: %s", ex.args[1])
            flash(message, category="error")
        else:
            logger.error(f"location_delete() Exception is: %s", ex.args[1])
            flash(ex.args[1], category="error")
    finally:
        con.close()
    return redirect(url_for('location_add_delete_query'))


# product move
@app.route('/productmove', methods=['GET', 'POST'])
def productmove():
    existing_qty = 0
    message = ""
    if request.method == "POST":
        try:
            pro_id = request.form['product_id']
            date_time = request.form['date']
            from_loc = request.form['from_location']
            to_loc = request.form['to_location']
            qty = request.form['qty']
            if len(to_loc) > 1:
                con = mysql.connection.cursor()
                existing_qty_sql = "select qty from productmovements where product_id=%s and length(to_location) = 0 "
                con.execute(existing_qty_sql, [pro_id])
                if(con.rowcount == 1):
                    existing_qty_dic = con.fetchone()
                    existing_qty = existing_qty_dic.get('qty')
                    if(int(existing_qty) >= int(qty)):
                        con = mysql.connection.cursor()
                        sql_update = "update productmovements set qty = %s where product_id = %s and from_location = %s and to_location = %s"
                        con.execute(sql_update, [int(existing_qty)-int(qty), pro_id, from_loc, to_loc])
                        sql_insert = "insert into productmovements (product_id,date_time,from_location,to_location,qty) value(%s,%s,%s,%s,%s)"
                        con.execute(sql_insert, [pro_id, date_time, from_loc, to_loc, qty])
                        mysql.connection.commit()
                        if(con.rowcount == 1):
                            message = f"The products '{pro_id}' is moved successfully"
                            logger.debug(f"productmove()%s",message)
                            flash(message, category="message")
                        return redirect(url_for('productmove'))
                    elif (existing_qty <= qty):
                        sql_update = "update productmovements set qty = 0 where movement_id = %s"
                        sql_insert = "insert into productmovements (product_id,date_time,from_location,to_location,existing_quantity - qty) value(%s,%s,%s,%s,%s)"
                        con.execute(sql_update[pro_id, date_time, from_loc, to_loc, qty],sql_insert[pro_id, date_time, from_loc, to_loc, qty])
                        mysql.connection.commit()
                        if(con.rowcount == 1):
                            message = f"The products '{pro_id}' is moved successfully"
                            logger.debug(f"productmove()%s",message)
                            flash(message, category="message")
                        return redirect(url_for('productmove'))
                else:
                    message = f"The products '{pro_id}' is not available in the product list, please add it as a new product in the 'Add Product' screen."
                    logger.debug(f"productmove() Exception is: %s", ex.args[1])
                    flash(message, category="message")
                    return redirect(url_for('productmove'))
            else:
                try:
                    con = mysql.connection.cursor()
                    sql = "INSERT INTO productmovements(product_id,date_time,from_location,to_location,qty) value(%s,%s,%s,%s,%s)"
                    con.execute(sql, [pro_id, date_time, from_loc, to_loc, qty])
                    mysql.connection.commit()
                    message = f"The products '{pro_id}' is moved successfully"
                    logger.debug(f"productmove()%s",message)
                    flash(message, category="message")
                except MySQLError as insertEx:
                    if("foreign key constraint fails" in insertEx.args[1]):
                        message = f"The product '{pro_id}' is not available for movement. Please add it to the list of products, before proceed with stock/movement."
                        logger.error(f"productmove() Exception is: %s", insertEx.args[1])
                        flash(message, category="message")
                    else:
                        logger.error(f"productmove() Exception is: %s", insertEx.args[1])
                        flash(insertEx.args[1], category="error")
                finally:
                    con.close()

            return redirect(url_for('productmove'))
        except MySQLError as ex:
            if("Duplicate" in ex.args[1]):
                message = f"The product {pro_id} is exists already.you can move product.."
                flash(message, category="message")
                logger.error(f"productmove() Exception is: %s", ex.args[1])
            else:
                logger.error(f"productmove() Exception is: %s", ex.args[1])
                flash(ex.args[1], category="error")
            return render_template('product_movement.html')
        finally:
            con.close()
    return render_template('product_movement.html')

#producmovement fetch query for update operation
@app.route('/productmove_update_query')
def productmove_update_query():
    try:
        con = mysql.connection.cursor()
        sql = "select * from productmovements"
        con.execute(sql)
        res = con.fetchall()
        logger.debug(f"Total no.of Product move available is %s",con.rowcount)
    except MySQLError as ex:
        logger.error(f"productmove_update_query() Database Exception occured:%s",ex.args[1])
    finally:
        con.close()
    return render_template('productmove_update_query.html', datas=res)

# product_move_update query
@app.route("/product_move_update/<string:movement_id>", methods=['GET', 'POST'])
def product_move_update(movement_id):
    con = mysql.connection.cursor()
    message = ""
    if request.method == 'POST':
        product_id = request.form['product_id']
        date_time = request.form['date_time']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        qty = request.form['qty']
        try:
            sql = "update productmovements set product_id = %s, date_time = %s, from_location = %s, to_location = %s, qty = %s where movement_id = %s"
            logger.debug(f"product_move_update() update query is: %s %s %s %s %s",
                         sql, product_id, date_time, from_location,to_location, qty)
            con.execute(sql, [product_id, date_time,
                        from_location, to_location, qty, movement_id])
            mysql.connection.commit()
            if(con.rowcount == 1):
                message = f" '{product_id}' Product Movement updated successfully.."
                logger.debug(f"product_move_update() %s",message)
                flash(message, category="message")
        except MySQLError as ex:
            logger.error("product_move_update() Database Exception Occured: %s",ex.args[1])
        finally:
            con.close()
        return redirect(url_for('productmove_update_query'))

    con = mysql.connection.cursor()
    sql = "select movement_id, product_id, DATE(date_time) as date_time, from_location, to_location, qty from productmovements where movement_id = %s"
    con.execute(sql, [movement_id])
    result = con.fetchone()
    return render_template('productmove_update.html', datas=result)

# productmove view query for delete operation
@app.route('/productmove_delete_query')
def productmove_delete_query():
    try:
        con = mysql.connection.cursor()
        sql = "select * from productmovements"
        con.execute(sql)
        res = con.fetchall()
        logger.debug(f"Total no.of Product movements delete available is %s",con.rowcount)
    except MySQLError as ex:
        logger.error("productmove-delete_query() Database Exception Occured:%s",ex.args[1])
    finally:
        con.close()
    return render_template('productmove_delete_query.html', datas=res)

# product_move_delete query
@app.route('/product_move_delete/<string:movement_id>', methods=['GET', 'POST'])
def product_move_delete(movement_id):
    message = ""
    try:
        con = mysql.connection.cursor()
        sql = "delete from productmovements where movement_id = %s"
        con.execute(sql, [movement_id])
        mysql.connection.commit()
        if(con.rowcount == 1):
            message = f"The product stock is deleted successfully."
            logger.debug("")
            flash(message, category="message")
            logger.debug(f"product_move_delete() %s",message)
        return redirect(url_for('productmove_delete_query'))
    except MySQLError as ex:
        logger.error("product_move_delete() Database Exception Occured:%s",ex.args[1])
        flash(ex.args[1], category="error")
    finally:
        con.close()
    return redirect(url_for('productmove_delete_query'))


# product_move_fetch query
@app.route('/product_move_fetch_query')
def product_move_fetch_query():
    try:
        con = mysql.connection.cursor()
        sql = "select * from productmovements"
        con.execute(sql)
        result = con.fetchall()
        logger.debug(f"Total no.of Product move available is %s",con.rowcount)
    except MySQLError as ex:
        logger.error("product_move_fetch_qury() Database Exception Occured : %s",ex.args[1])
    finally:
        con.close()
    return render_template('product_movement.html', datas=result)


# report_fetch query
@app.route('/report')
def report_page():
    try:
        con = mysql.connection.cursor()
        sql = "select product_id, from_location as location, max(qty) as qty from productmovements where length(to_location)=0 group by from_location, product_id order by from_location asc;"
        con.execute(sql)
        result = con.fetchall()
        sql = "select product_id, to_location as location, max(qty) as qty from productmovements where length(to_location)>1 group by to_location, product_id order by to_location asc;"
        con.execute(sql)
        result1 = con.fetchall()
        logger.debug(f"report_page() %s warehouse/stocks reports",con.rowcount)
    except MySQLError as ex:
        logger.error(f"report_page() Databse Exception Occured: %s",ex.args[1])
        logger.error(f" '{result}'")
        logger.error(f" '{result1}'")
    finally:
        con.close()
    return render_template('report.html', datas=result+result1)

# view query of product add data
@app.route('/product_add_data_view')
def product_add_data_view():
    try:
        con = mysql.connection.cursor()
        sql = "select * from products"
        con.execute(sql)
        res = con.fetchall()
        logger.debug(f"product_add_data_view() %s products available",con.rowcount)
    except MySQLError as ex:
        flash(ex.args[1], category="error")   
        logger.error(f"product_add_data_view() Database Exception Occured: %s",ex.args[1])
    finally:
        con.close()
    return render_template('product_data_view.html', datas=res)


@app.route('/location_data_view')
def location_data_view():
    try:
        con = mysql.connection.cursor()
        sql = "select * from location"
        con.execute(sql)
        res = con.fetchall()
        logger.debug(f"location_data_view() %s location available",con.rowcount)
    except MySQLError as ex:
        logger.error(f"location_data_view() Database Exception Occured: %s",ex.args[1])
    finally:
        con.close()
    return render_template('location_data_view.html', datas=res)


@app.route('/productmove_data_view')
def productmove_data_view():
    try:
        con = mysql.connection.cursor()
        sql = "select * from productmovements"
        con.execute(sql)
        res = con.fetchall()
        logger.debug(f"producmove_data_view() %s product movements available",con.rowcount)
    except MySQLError as ex:
        logger.error("productmove_data_view() Database Exception Occured: %s",ex.args[1])
    finally:
        con.close()
    return render_template('productmove_data_view.html', datas=res)


if __name__ == "__main__":
    app.secret_key = "pandi"
    app.run(debug=True)