from flask import Flask, jsonify, render_template, request
import sqlite3 as sql
import pandas as pd
import io
import matplotlib.pyplot as plt
import base64
import seaborn as sns  # สร้าง กราฟ
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search', methods=['GET', 'POST'])
def searchorder():
    tablename = "Orders"
    if 'PROD_CODE' in request.values:
        print('XXX', request.values['PROD_CODE'])
        pcode = request.values['PROD_CODE']
        with sql.connect("database.db") as con:
            c = con.cursor()
            c.execute(
                "SELECT PROD_CODE, cust_code, store_code  FROM orders WHERE PROD_CODE='" + pcode + "' LIMIT 0,100")
            rows = c.fetchall()
            return render_template('searchorder.html', rows=rows, tb=tablename)
    else:
        return render_template('searchorder.html', tb=tablename)


@app.route('/product/insert/form', methods=['GET', 'POST'])
def insertproductform():
    return render_template('insertproductform.html')


@app.route('/product/insert/', methods=['GET', 'POST'])
def insertproduct():
    if request.values:
        pid = request.values['pid']
        pname = request.values['pname']
        price = request.values['price']
        with sql.connect("database.db") as con:
            c = con.cursor()
            s = "INSERT INTO PRODUCTS VALUES ('" + \
                pid + "','" + pname + "','" + price + "')"
            c.execute(s)
            return render_template('home.html')


@app.route('/product/select/', methods=['GET', 'POST'])
def searchproduct():
    return render_template('searchproduct.html')


@app.route('/product/select/ajax', methods=['GET', 'POST'])
def searchproductajax():

    if request.values:
        page = int(request.values['page'])
        per_page = 50
        offset = page * per_page
        with sql.connect("database.db") as con:
            c = con.cursor()
            c.execute("SELECT *  FROM Products LIMIT " +
                      str(offset) + "," + str(per_page))
            rows = c.fetchall()
            print('test')
            return render_template('producttable.html', rows=rows)


@app.route('/product/edit/form', methods=['GET', 'POST'])
def editproductform():
    if request.values:
        pid = request.values['pid']
        pname = request.values['pname']
        price = request.values['price']
    return render_template('editproductform.html', pid=pid, pname=pname, price=price)


@app.route('/product/edit/', methods=['GET', 'POST'])
def editproduct():
    pid = ''
    pname = ''
    price = ''
    if request.values:
        pid = request.values['pid']
        pname = request.values['pname']
        price = request.values['price']
        if pname == "":
            return render_template('searchproduct.html')
        if price == "":
            return render_template('searchproduct.html')
        with sql.connect("database.db") as con:
            c = con.cursor()
            s = "UPDATE products SET product_name ='" + pname + \
                "', price ='" + price+"' WHERE  product_id = '" + pid + "'"
            c.execute(s)
            return render_template('home.html', pid=pid, pname=pname, price=price)
            # return render_template('editproductform.html',pid=pid,pname=pname,price=price)


@app.route('/product/delete', methods=['GET', 'POST'])
def deleteproduct():
    if request.values:
        pid = request.values['pid']
        with sql.connect("database.db") as con:
            c = con.cursor()
            s = "DELETE FROM PRODUCTS WHERE product_id = '" + pid + "'"
            c.execute(s)
            return render_template('searchproduct.html')


@app.route('/genPDF', methods=['GET', 'POST'])
def genpdf():
    return render_template('genpdf.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    store_code = 'STORE00001'
    if request.values:
        store_code = request.values['sid']
    amount = 0
    with sql.connect("database.db") as con:
        c = con.cursor()
        s = "SELECT SUM(spend) FROM orders WHERE STORE_CODE = '" + \
            store_code + "'"
        c.execute(s)
        amount = c.fetchone()[0]

        s = "SELECT SHOP_DATE, sum(spend) as amount FROM orders WHERE STORE_CODE = '" + \
            store_code + "' GROUP BY SHOP_DATE "
        result = c.execute(s)
        sqldf = pd.DataFrame()
        img = io.BytesIO()
        for row in result:
            sd = row[0] % 100
            amount = row[1]
            row_sql = {"SHOP_DATE": sd, "amount": amount}
            # sqldf.append(row)
            sqldf = sqldf.append(row_sql, ignore_index=True)
        plt.figure()
        sns_plot = sns.lineplot(x='SHOP_DATE', y='amount',
                                data=sqldf, label='Amount')  # พล็อต
        fig = sns_plot.get_figure()
        fig.savefig(img, format='png')
        plot1 = base64.b64encode(img.getvalue()).decode()

        s = "SELECT CUST_CODE FROM orders WHERE STORE_CODE = '" + store_code + "'"
        result = c.execute(s)
        sqldf = pd.DataFrame()
        img2 = io.BytesIO()
        for row in result:
            row_sql = {"CUST_CODE": row[0]}
            # sqldf.append(row)
            sqldf = sqldf.append(row_sql, ignore_index=True)
        plt.figure()
        sns_plot2 = sns.countplot(x="CUST_CODE", data=sqldf)  # พล็อต
        fig2 = sns_plot2.get_figure()
        fig2.savefig(img2, format='png')
        plot2 = base64.b64encode(img2.getvalue()).decode()

        s = "SELECT STORE_CODE, SHOP_DATE , SUM(SPEND) as AMOUNT"\
            " FROM orders "\
            " WHERE STORE_CODE = '" + store_code + "'"\
            " GROUP BY STORE_CODE, SHOP_DATE  "\
            " ORDER BY STORE_CODE  "
        result = c.execute(s)
        sqldf = pd.DataFrame()
        img3 = io.BytesIO()
        row_list = []
        for row in result:
            c1 = row[0]  
            c2 = row[1]
            c3 = row[2]
            row_sql = {'STORE_CODE' : c1, 'SHOP_DATE' : c2 ,  'AMOUNT' :  c3 }
            # sqldf.append(row)
            sqldf = sqldf.append(row_sql, ignore_index=True)
        plt.figure()
        sns_plot3 = sns.barplot(x="SHOP_DATE", y="AMOUNT", data=sqldf)  # พล็อต
        fig3 = sns_plot3.get_figure()
        fig3.savefig(img3, format='png')
        plot3 = base64.b64encode(img3.getvalue()).decode()

        s = "SELECT STORE_CODE, SHOP_DATE , SUM(SPEND) as AMOUNT"\
            " FROM orders "\
            " WHERE STORE_CODE = '" + store_code + "'"\
            " GROUP BY STORE_CODE, SHOP_DATE  "\
            " ORDER BY STORE_CODE  "
        result = c.execute(s)
        sqldf = pd.DataFrame()
        img4 = io.BytesIO()
        row_list = []
        for row in result:
            c1 = row[0]  
            c2 = row[1]
            c3 = row[2]
            row_sql = {'STORE_CODE' : c1, 'SHOP_DATE' : c2 ,  'AMOUNT' :  c3 }
            # sqldf.append(row)
            sqldf = sqldf.append(row_sql, ignore_index=True)
        plt.figure()
        ax = fig.add_axes([0,0,1,1])
        ax.pie(sqldf['AMOUNT'], labels = sqldf['SHOP_DATE'],autopct='%1.2f%%') #แก้ที่นี่
        fig4 = ax.get_figure()
        fig4.savefig(img4, format='png')
        plot4 = base64.b64encode(img4.getvalue()).decode()

        return render_template('dashboard.html', c1=c1, c2=c2,  amount=amount, plot1=plot1, plot2=plot2, plot3=plot3, plot4=plot4)

    # return render_template('dashboard.html')


@app.route('/customer', methods=['GET', 'POST'])
def searchcustomer():
    tablename = "Customers"
    if 'CUST_CODE' in request.values:
        print('XXX', request.values['CUST_CODE'])
        ccode = request.values['CUST_CODE']
        with sql.connect("database.db") as con:
            c = con.cursor()
            c.execute(
                "SELECT customers.CUST_CODE, customers.CUST_NAME, customers.CUST_LIFESTAGE, customers.CUST_PRICE_SENSITIVITY, orders.BASKET_ID, orders.STORE_CODE,  products.product_id FROM orders INNER JOIN customers ON orders.CUST_CODE = customers.CUST_CODE INNER JOIN products ON orders.PROD_CODE = products.product_id WHERE customers.CUST_CODE='" + ccode + "' GROUP BY customers.CUST_CODE;")
            rows = c.fetchall()
            return render_template('customer.html', rows=rows, tb=tablename)
    else:
        return render_template('customer.html', tb=tablename)


@app.route('/customer/basket', methods=['GET', 'POST'])
def searchcustomerbasket():
    tablename = "Orders"
    if 'BASKET_ID' in request.values:
        print('XXX', request.values['BASKET_ID'])
        bid = request.values['BASKET_ID']
        with sql.connect("database.db") as con:
            c = con.cursor()
            c.execute(
                "SELECT customers.CUST_CODE, customers.CUST_NAME, customers.CUST_LIFESTAGE, customers.CUST_PRICE_SENSITIVITY, orders.BASKET_ID, orders.STORE_CODE,  products.product_id FROM orders INNER JOIN customers ON orders.CUST_CODE = customers.CUST_CODE INNER JOIN products ON orders.PROD_CODE = products.product_id WHERE orders.BASKET_ID='" + bid + "' GROUP BY customers.CUST_CODE;")
            rows = c.fetchall()
            return render_template('customer.html', rows=rows, tb=tablename)
    else:
        return render_template('customer.html', tb=tablename)


@app.route('/customer/store', methods=['GET', 'POST'])
def searchcustomerstore():
    tablename = "Orders"
    if 'STORE_CODE' in request.values:
        print('XXX', request.values['STORE_CODE'])
        scode = request.values['STORE_CODE']
        with sql.connect("database.db") as con:
            c = con.cursor()
            c.execute(
                "SELECT customers.CUST_CODE, customers.CUST_NAME, customers.CUST_LIFESTAGE, customers.CUST_PRICE_SENSITIVITY, orders.BASKET_ID, orders.STORE_CODE,  products.product_id FROM orders INNER JOIN customers ON orders.CUST_CODE = customers.CUST_CODE INNER JOIN products ON orders.PROD_CODE = products.product_id WHERE orders.STORE_CODE='" + scode + "' GROUP BY customers.CUST_CODE;")
            rows = c.fetchall()
            return render_template('customer.html', rows=rows, tb=tablename)
    else:
        return render_template('customer.html', tb=tablename)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
