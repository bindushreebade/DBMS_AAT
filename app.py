from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import os
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('add_user'))

    cur = mysql.connection.cursor()

    # Get current user
    cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()

    # Get all products
    cur.execute("SELECT * FROM products WHERE user_id = %s", (session['user_id'],))
    products = cur.fetchall()

    # Calculate totals
    total_products = len(products)
    total_cost = sum(product[2] for product in products) if products else 0
    discount = float(session.get('discount', 0))
    discounted_total = total_cost * (1 - discount / 100)

    cur.close()

    return render_template('index.html', 
                         products=products, 
                         total_products=total_products, 
                         total_cost=total_cost,
                         discounted_total=discounted_total,
                         discount=discount,
                         user=user)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        return redirect(url_for('add_user'))

    if request.method == 'POST':
        name = request.form['name']
        cost = float(request.form['cost'])

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO products (name, cost, user_id) VALUES (%s, %s, %s)", 
                   (name, cost, session['user_id']))
        mysql.connection.commit()
        cur.close()

        flash('Product added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_product.html')

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if 'user_id' not in session:
        return redirect(url_for('add_user'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        cost = float(request.form['cost'])

        cur.execute("UPDATE products SET name = %s, cost = %s WHERE id = %s AND user_id = %s", 
                   (name, cost, id, session['user_id']))
        mysql.connection.commit()
        cur.close()

        flash('Product updated successfully!', 'success')
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM products WHERE id = %s AND user_id = %s", (id, session['user_id']))
    product = cur.fetchone()
    cur.close()

    if not product:
        flash('Product not found!', 'danger')
        return redirect(url_for('index'))

    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:id>')
def delete_product(id):
    if 'user_id' not in session:
        return redirect(url_for('add_user'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id = %s AND user_id = %s", (id, session['user_id']))
    mysql.connection.commit()
    cur.close()

    flash('Product deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/apply_discount', methods=['POST'])
def apply_discount():
    discount = float(request.form['discount'])
    session['discount'] = discount
    flash(f'Discount of {discount}% applied to all products!', 'success')
    return redirect(url_for('index'))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_pic = filename
            else:
                profile_pic = 'default.png'
        else:
            profile_pic = 'default.png'

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, profile_pic) VALUES (%s, %s, %s)", 
                   (username, email, profile_pic))
        mysql.connection.commit()

        # Get the inserted user's ID
        cur.execute("SELECT LAST_INSERT_ID()")
        user_id = cur.fetchone()[0]
        cur.close()

        session['user_id'] = user_id
        flash('User profile created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_user.html')

if __name__ == '__main__':
    app.run(debug=True)
