from flask import Flask, render_template, request, redirect, session
import sqlite3

class Item:
    def __init__(self, row):
        self.id = row[0]
        self.name = row[1]
        self.description = row[2]
        self.category = row[3]
        self.total = row[4]
        self.available = row[5]
        self.checked_out = row[6]

app = Flask(__name__)
app.secret_key = "secret123"


# ✅ Inject department globally (no need to pass to templates)
@app.context_processor
def inject_department():
    return dict(department=session.get('department'))


# ✅ HOME ROUTES
@app.route('/')
def home():
    return redirect('/login')


@app.route('/login')
def login():
    if 'department' in session:
        return redirect('/home-page')
    return render_template('login.html')


@app.route('/set-department', methods=['POST'])
def set_department():
    department = request.form['department']

    if department == "":
        return "Please select a department"

    session['department'] = department
    return redirect('/home-page')


@app.route('/home-page')
def home_page():
    if 'department' not in session:
        return redirect('/login')
    return render_template('index.html')


# ✅ INVENTORY PAGE
@app.route('/inventory', methods=['GET'])
def inventory():
    if 'department' not in session:
        return redirect('/login')

    search = request.args.get('search')
    
    if search == "" or search == "None":
        search = None


    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if search:
        cursor.execute("""
            SELECT * FROM inventory
            WHERE name LIKE ? OR category LIKE ?
        """, ('%' + search + '%', '%' + search + '%'))
    else:
        cursor.execute("SELECT * FROM inventory")


    rows = cursor.fetchall()
    items = [Item(row) for row in rows]
    conn.close()

    return render_template('inventory.html', items=items, search=search)


# ✅ RETURN ITEM (POST)
@app.route('/return', methods=['POST'])
def return_item():
    if 'department' not in session:
        return redirect('/login')

    item_id = request.form['item_id']
    quantity_input = request.form['quantity']

    if quantity_input == "":
        return "Please enter a quantity"

    # ✅ SAFE conversion
    try:
        quantity = int(quantity_input)
    except:
        return "Invalid quantity"

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT available_quantity, checked_out_quantity 
        FROM inventory 
        WHERE id=?
    """, (item_id,))
    
    item = cursor.fetchone()

    available = item[0]
    checked_out = item[1]

    if quantity <= 0 or quantity > checked_out:
        conn.close()
        return "Invalid return quantity"

    new_available = available + quantity
    new_checked_out = checked_out - quantity

    cursor.execute("""
        UPDATE inventory
        SET available_quantity = ?, checked_out_quantity = ?
        WHERE id = ?
    """, (new_available, new_checked_out, item_id))

    cursor.execute("""
        INSERT INTO transactions (item_id, action, quantity, department)
        VALUES (?, 'return', ?, ?)
    """, (item_id, quantity, session['department']))

    conn.commit()
    conn.close()

    return redirect('/return-page?msg=returned')


# ✅ RETURN PAGE
@app.route('/return-page')
def return_page():
    if 'department' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.id, i.name,
            COALESCE(SUM(CASE 
                WHEN t.action = 'checkout' THEN t.quantity
                WHEN t.action = 'return' THEN -t.quantity
            END), 0) AS checked_out
        FROM inventory i
        LEFT JOIN transactions t
            ON i.id = t.item_id
            AND t.department = ?
        GROUP BY i.id, i.name
    """, (session['department'],))

    items = cursor.fetchall()
    conn.close()

    return render_template('return.html', items=items)


# ✅ STATUS PAGE (SIMPLIFIED)
@app.route('/status')
def status():
    if 'department' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()

    conn.close()

    return render_template('status.html', items=items)


# ✅ TRANSACTIONS PAGE
@app.route('/transactions')
def transactions():
    if 'department' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.id, i.name, t.action, t.quantity, t.department, t.timestamp
        FROM transactions t
        JOIN inventory i ON t.item_id = i.id
        ORDER BY t.timestamp DESC
    """)

    data = cursor.fetchall()
    conn.close()

    return render_template('transactions.html', transactions=data)


# ✅ CART - ADD ITEM

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'department' not in session:
        return redirect('/login')

    item_id = request.form['item_id']
    quantity_input = request.form['quantity']
    search = request.form.get('search')  # ✅ get search ONCE

    # ✅ helper function for all redirects
    def redirect_inventory(msg=None, error=None):
        url = '/inventory?'

        params = []
        if msg:
            params.append(f'msg={msg}')
        if error:
            params.append(f'error={error}')
        if search:
            params.append(f'search={search}')

        url += "&".join(params)
        return redirect(url)

    # ✅ validation: empty
    if quantity_input == "":
        return redirect_inventory(error='invalid_qty')

    # ✅ validation: not a number
    try:
        quantity = int(quantity_input)
    except:
        return redirect_inventory(error='invalid_qty')

    # ✅ database lookup
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, available_quantity FROM inventory WHERE id=?",
        (item_id,)
    )
    item = cursor.fetchone()
    conn.close()

    available = item[1]

    # ✅ validation logic (ALL using redirect helper)
    if available == 0:
        return redirect_inventory(error='no_stock')

    if quantity <= 0:
        return redirect_inventory(error='invalid_qty')

    if quantity > available:
        return redirect_inventory(error='exceeds')

    # ✅ CART LOGIC
    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    found = False

    for existing_item in cart:
        if str(existing_item['id']) == str(item_id):
            new_quantity = existing_item['quantity'] + quantity

            if new_quantity > existing_item['available']:
                return redirect_inventory(error='exceeds')

            existing_item['quantity'] = new_quantity
            found = True
            break

    if not found:
        cart.append({
            "id": item_id,
            "name": item[0],
            "quantity": quantity,
            "available": available
        })

    session['cart'] = cart

    # ✅ success redirect (same system)
    return redirect_inventory(msg='added')



# ✅ CHECKOUT PAGE
@app.route('/checkout-page')
def checkout_page():
    if 'department' not in session:
        return redirect('/login')

    cart = session.get('cart', [])
    return render_template('checkout.html', cart=cart)


# ✅ FINALIZE CHECKOUT
@app.route('/finalize-checkout', methods=['POST'])
def finalize_checkout():
    if 'department' not in session:
        return redirect('/login')

    cart = session.get('cart', [])

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    for item in cart:
        item_id = item['id']
        quantity = int(item['quantity'])

        cursor.execute("""
            SELECT available_quantity, checked_out_quantity 
            FROM inventory 
            WHERE id=?
        """, (item_id,))
        
        db_item = cursor.fetchone()

        available = db_item[0]
        checked_out = db_item[1]

        if quantity > available:
            conn.close()
            return "Invalid quantity in cart"

        new_available = available - quantity
        new_checked_out = checked_out + quantity

        cursor.execute("""
            UPDATE inventory
            SET available_quantity = ?, checked_out_quantity = ?
            WHERE id = ?
        """, (new_available, new_checked_out, item_id))

        cursor.execute("""
            INSERT INTO transactions (item_id, action, quantity, department)
            VALUES (?, 'checkout', ?, ?)
        """, (item_id, quantity, session['department']))

    conn.commit()
    conn.close()

    session.pop('cart', None)

    return redirect('/home-page?msg=checkout')


# ✅ REMOVE ITEM FROM CART
@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    if 'department' not in session:
        return redirect('/login')

    item_id = request.form['item_id']

    cart = session.get('cart', [])
    cart = [item for item in cart if str(item['id']) != str(item_id)]

    session['cart'] = cart

    return redirect('/checkout-page')


# ✅ UPDATE CART (+ / -)
@app.route('/update-cart', methods=['POST'])
def update_cart():
    if 'department' not in session:
        return redirect('/login')

    item_id = request.form['item_id']
    action = request.form['action']

    cart = session.get('cart', [])

    for item in cart:
        if str(item['id']) == str(item_id):

            if action == "increase":
                if item['quantity'] < item['available']:
                    item['quantity'] += 1

            elif action == "decrease":
                if item['quantity'] > 1:
                    item['quantity'] -= 1

    session['cart'] = cart

    return redirect('/checkout-page')


# ✅ MANUAL CART EDIT
@app.route('/update-cart-quantity', methods=['POST'])
def update_cart_quantity():
    if 'department' not in session:
        return redirect('/login')

    item_id = request.form['item_id']
    quantity_input = request.form['quantity']

    try:
        quantity = int(quantity_input)
    except:
        return "Invalid quantity"

    cart = session.get('cart', [])

    for item in cart:
        if str(item['id']) == str(item_id):

            if quantity <= 0:
                cart.remove(item)
                break

            if quantity > item['available']:
                quantity = item['available']

            item['quantity'] = quantity
            break

    session['cart'] = cart

    return redirect('/checkout-page')

@app.route('/add-item-future')
def add_item_future():
    return render_template('add_item_future.html')

@app.route('/checked-out-items')
def checked_out_items():
    if 'department' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            inventory.name,
            transactions.department,
            SUM(CASE 
                WHEN transactions.action = 'checkout' THEN transactions.quantity
                WHEN transactions.action = 'return' THEN -transactions.quantity
            END) as net_quantity
        FROM transactions
        JOIN inventory
            ON transactions.item_id = inventory.id
        GROUP BY inventory.name, transactions.department
        HAVING net_quantity > 0
        ORDER BY transactions.department, inventory.name
    """)

    items = cursor.fetchall() or []
    conn.close()

    return render_template('checked_out_items.html', items=items)

# ✅ LOGOUT
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('department', None)
    session.pop('cart', None)
    return redirect('/login')

# ✅ RUN APP
if __name__ == '__main__':
    app.run(debug=True) #local
    #app.run(host='0.0.0.0', port=10000, debug=True) #production
