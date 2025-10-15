from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector

app = Flask(__name__)

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",              
    password="@0706647669J", #replace wih ur MySQL workbench password
    database="rental_management"
)
cursor = db.cursor(dictionary=True)


# Dashboard (Home)
@app.route('/')
def index():
    return render_template('index.html')


# Tenants CRUD
@app.route('/tenants')
def tenants():
    cursor.execute("SELECT * FROM tenant")
    tenants = cursor.fetchall()
    return render_template('tenants.html', tenants=tenants)

@app.route('/add_tenant', methods=['POST'])
def add_tenant():
    name = request.form['name']
    number = request.form['number']
    contact = request.form['contact']
    cursor.execute(
        "INSERT INTO tenant (tenant_name, tenant_number, tenant_contact) VALUES (%s, %s, %s)",
        (name, number, contact)
    )
    db.commit()
    return redirect(url_for('tenants'))

@app.route('/delete_tenant/<int:tenant_id>')
def delete_tenant(tenant_id):
    cursor.execute("DELETE FROM tenant WHERE tenant_id = %s", (tenant_id,))
    db.commit()
    return redirect(url_for('tenants'))

@app.route('/edit_tenant/<int:tenant_id>', methods=['GET', 'POST'])
def edit_tenant(tenant_id):
    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        contact = request.form['contact']
        cursor.execute(
            "UPDATE tenant SET tenant_name=%s, tenant_number=%s, tenant_contact=%s WHERE tenant_id=%s",
            (name, number, contact, tenant_id)
        )
        db.commit()
        return redirect(url_for('tenants'))
    else:
        cursor.execute("SELECT * FROM tenant WHERE tenant_id = %s", (tenant_id,))
        tenant = cursor.fetchone()
        return render_template('edit_tenant.html', tenant=tenant)

# Filter: Top Paying Tenants
@app.route('/top_tenants')
def top_tenants():
    query = """
        SELECT t.tenant_name, SUM(tr.amount) AS total_paid
        FROM tenant t
        JOIN lease l ON t.tenant_id = l.tenant_id
        JOIN transactions tr ON l.lease_id = tr.lease_id
        GROUP BY t.tenant_id
        ORDER BY total_paid DESC
        LIMIT 5;
    """
    cursor.execute(query)
    tenants = cursor.fetchall()
    return render_template('top_tenants.html', tenants=tenants)


# Rooms CRUD
@app.route('/rooms')
def rooms():
    cursor.execute("""
        SELECT r.*, pm.manager_name 
        FROM room r 
        JOIN property_manager pm ON r.manager_id = pm.manager_id
    """)
    rooms = cursor.fetchall()

    # Managers for dropdowns
    cursor.execute("SELECT * FROM property_manager")
    managers = cursor.fetchall()

    return render_template('rooms.html', rooms=rooms, managers=managers)

@app.route('/add_room', methods=['POST'])
def add_room():
    manager_id = request.form['manager_id']
    current_user_number = request.form['current_user_number']
    monthly_fee = request.form['monthly_fee']
    maximum_users = request.form['maximum_users']
    cursor.execute(
        "INSERT INTO room (manager_id, current_user_number, monthly_fee, maximum_users) VALUES (%s, %s, %s, %s)",
        (manager_id, current_user_number, monthly_fee, maximum_users)
    )
    db.commit()
    return redirect(url_for('rooms'))

@app.route('/delete_room/<int:room_id>')
def delete_room(room_id):
    cursor.execute("DELETE FROM room WHERE room_id = %s", (room_id,))
    db.commit()
    return redirect(url_for('rooms'))

@app.route('/edit_room/<int:room_id>', methods=['GET', 'POST'])
def edit_room(room_id):
    if request.method == 'POST':
        manager_id = request.form['manager_id']
        current_user_number = request.form['current_user_number']
        monthly_fee = request.form['monthly_fee']
        maximum_users = request.form['maximum_users']
        cursor.execute(
            "UPDATE room SET manager_id=%s, current_user_number=%s, monthly_fee=%s, maximum_users=%s WHERE room_id=%s",
            (manager_id, current_user_number, monthly_fee, maximum_users, room_id)
        )
        db.commit()
        return redirect(url_for('rooms'))
    else:
        cursor.execute("SELECT * FROM room WHERE room_id = %s", (room_id,))
        room = cursor.fetchone()
        cursor.execute("SELECT * FROM property_manager")
        managers = cursor.fetchall()
        return render_template('edit_room.html', room=room, managers=managers)


# Leases CRUD
@app.route('/leases')
def leases():
    cursor.execute("""
        SELECT l.*, t.tenant_name, r.room_id, r.monthly_fee
        FROM lease l
        JOIN tenant t ON l.tenant_id = t.tenant_id
        JOIN room r ON l.room_id = r.room_id
    """)
    leases = cursor.fetchall()

    cursor.execute("SELECT * FROM tenant")
    tenants = cursor.fetchall()
    cursor.execute("SELECT * FROM room")
    rooms = cursor.fetchall()

    return render_template('leases.html', leases=leases, tenants=tenants, rooms=rooms)

@app.route('/add_lease', methods=['POST'])
def add_lease():
    tenant_id = request.form['tenant_id']
    room_id = request.form['room_id']
    month_start = request.form['month_start']
    total_months = request.form['total_months']
    percentage_cleared = request.form['percentage_cleared']
    cursor.execute(
        "INSERT INTO lease (tenant_id, room_id, month_start, total_number_of_months, percentage_cleared) VALUES (%s, %s, %s, %s, %s)",
        (tenant_id, room_id, month_start, total_months, percentage_cleared)
    )
    db.commit()
    return redirect(url_for('leases'))

@app.route('/delete_lease/<int:lease_id>')
def delete_lease(lease_id):
    cursor.execute("DELETE FROM lease WHERE lease_id = %s", (lease_id,))
    db.commit()
    return redirect(url_for('leases'))

@app.route('/edit_lease/<int:lease_id>', methods=['GET', 'POST'])
def edit_lease(lease_id):
    if request.method == 'POST':
        tenant_id = request.form['tenant_id']
        room_id = request.form['room_id']
        month_start = request.form['month_start']
        total_months = request.form['total_months']
        percentage_cleared = request.form['percentage_cleared']
        cursor.execute(
            "UPDATE lease SET tenant_id=%s, room_id=%s, month_start=%s, total_number_of_months=%s, percentage_cleared=%s WHERE lease_id=%s",
            (tenant_id, room_id, month_start, total_months, percentage_cleared, lease_id)
        )
        db.commit()
        return redirect(url_for('leases'))
    else:
        cursor.execute("SELECT * FROM lease WHERE lease_id = %s", (lease_id,))
        lease = cursor.fetchone()
        cursor.execute("SELECT * FROM tenant")
        tenants = cursor.fetchall()
        cursor.execute("SELECT * FROM room")
        rooms = cursor.fetchall()
        return render_template('edit_lease.html', lease=lease, tenants=tenants, rooms=rooms)
    

# Transactions CRUD
@app.route('/transactions')
def transactions():
    filter_type = request.args.get('filter', 'all')
    month_filter = request.args.get('month', '')

    base_query = """
        SELECT tr.*, t.tenant_name, r.room_id, l.total_number_of_months, r.monthly_fee
        FROM transactions tr
        JOIN lease l ON tr.lease_id = l.lease_id
        JOIN tenant t ON l.tenant_id = t.tenant_id
        JOIN room r ON l.room_id = r.room_id
    """

    where_clauses = []
    params = []

    if filter_type == 'unpaid':
        # Subquery to get leases with balance > 0
        base_query += """
            JOIN (
                SELECT l2.lease_id,
                       (l2.total_number_of_months * r2.monthly_fee) - IFNULL(SUM(tr2.amount), 0) AS balance
                FROM lease l2
                JOIN room r2 ON l2.room_id = r2.room_id
                LEFT JOIN transactions tr2 ON l2.lease_id = tr2.lease_id
                GROUP BY l2.lease_id
                HAVING balance > 0
            ) bal ON l.lease_id = bal.lease_id
        """
    elif filter_type == 'month' and month_filter:
        where_clauses.append("DATE_FORMAT(tr.transaction_date, '%Y-%m') = %s")
        params.append(month_filter)

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    cursor.execute(base_query, params)
    transactions = cursor.fetchall()

    # for add form → need leases to pick from
    cursor.execute("""
        SELECT l.lease_id, t.tenant_name, r.room_id
        FROM lease l
        JOIN tenant t ON l.tenant_id = t.tenant_id
        JOIN room r ON l.room_id = r.room_id
    """)
    leases = cursor.fetchall()

    return render_template('transactions.html', transactions=transactions, leases=leases, filter_type=filter_type, month_filter=month_filter)


# Add transaction
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    lease_id = request.form['lease_id']
    transaction_date = request.form['transaction_date']
    amount = request.form['amount']
    cursor.execute(
        "INSERT INTO transactions (lease_id, transaction_date, amount) VALUES (%s, %s, %s)",
        (lease_id, transaction_date, amount)
    )
    db.commit()
    return redirect(url_for('transactions'))


# Delete transaction
@app.route('/delete_transaction/<int:transaction_id>')
def delete_transaction(transaction_id):
    cursor.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
    db.commit()
    return redirect(url_for('transactions'))


# Edit transaction
@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    if request.method == 'POST':
        lease_id = request.form['lease_id']
        transaction_date = request.form['transaction_date']
        amount = request.form['amount']
        cursor.execute(
            "UPDATE transactions SET lease_id=%s, transaction_date=%s, amount=%s WHERE transaction_id=%s",
            (lease_id, transaction_date, amount, transaction_id)
        )
        db.commit()
        return redirect(url_for('transactions'))
    else:
        cursor.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
        transaction = cursor.fetchone()
        cursor.execute("""
            SELECT l.lease_id, t.tenant_name, r.room_id
            FROM lease l
            JOIN tenant t ON l.tenant_id = t.tenant_id
            JOIN room r ON l.room_id = r.room_id
        """)
        leases = cursor.fetchall()
        return render_template('edit_transaction.html', transaction=transaction, leases=leases)


# Report: Total payments & balances per tenant
@app.route('/transaction_report')
def transaction_report():
    query = """
        SELECT 
            t.tenant_name,
            r.room_id,
            (l.total_number_of_months * r.monthly_fee) AS total_due,
            IFNULL(SUM(tr.amount),0) AS total_paid,
            ((l.total_number_of_months * r.monthly_fee) - IFNULL(SUM(tr.amount),0)) AS balance
        FROM lease l
        JOIN tenant t ON l.tenant_id = t.tenant_id
        JOIN room r ON l.room_id = r.room_id
        LEFT JOIN transactions tr ON l.lease_id = tr.lease_id
        GROUP BY l.lease_id;
    """
    cursor.execute(query)
    report = cursor.fetchall()
    return render_template('transaction_report.html', report=report)

# Reports Dashboard
@app.route('/reports')
def reports():
    return render_template('reports.html')


# Monthly Rent Collection
@app.route('/report_monthly_collection')
def report_monthly_collection():
    query = """
        SELECT
            YEAR(transaction_date) AS year,
            MONTH(transaction_date) AS month,
            SUM(amount) AS total_collected
        FROM transactions
        GROUP BY YEAR(transaction_date), MONTH(transaction_date)
        ORDER BY year, month;
    """
    cursor.execute(query)
    report = cursor.fetchall()
    return render_template('report_monthly_collection.html', report=report)

@app.route('/api/monthly_collection')
def api_monthly_collection():
    month = request.args.get('month')

    if month:
        query = """
            SELECT
                YEAR(transaction_date) AS year,
                MONTH(transaction_date) AS month,
                SUM(amount) AS total_collected
            FROM transactions
            WHERE MONTH(transaction_date) = %s
            GROUP BY YEAR(transaction_date), MONTH(transaction_date)
            ORDER BY year, month
        """
        cursor.execute(query, (month,))
        data = cursor.fetchall()
    else:
        query = """
            SELECT
                YEAR(transaction_date) AS year,
                MONTH(transaction_date) AS month,
                SUM(amount) AS total_collected
            FROM transactions
            GROUP BY YEAR(transaction_date), MONTH(transaction_date)
            ORDER BY year, month
        """
        cursor.execute(query)
        data = cursor.fetchall()

    return jsonify({
        'labels': [f"{row['year']}-{row['month']:02d}" for row in data],
        'data': [row['total_collected'] for row in data]
    })


# Outstanding Balances
@app.route('/report_outstanding')
def report_outstanding():
    query = """
        SELECT 
            t.tenant_name,
            r.room_id,
            (l.total_number_of_months * r.monthly_fee) AS total_due,
            IFNULL(SUM(tr.amount),0) AS total_paid,
            ((l.total_number_of_months * r.monthly_fee) - IFNULL(SUM(tr.amount),0)) AS balance
        FROM lease l
        JOIN tenant t ON l.tenant_id = t.tenant_id
        JOIN room r ON l.room_id = r.room_id
        LEFT JOIN transactions tr ON l.lease_id = tr.lease_id
        GROUP BY l.lease_id
        HAVING balance > 0;
    """
    cursor.execute(query)
    report = cursor.fetchall()
    return render_template('report_outstanding.html', report=report)


# Manager Performance
@app.route('/report_manager_performance')
def report_manager_performance():
    query = """
        SELECT 
            pm.manager_name,
            SUM(tr.amount) AS total_collected
        FROM property_manager pm
        JOIN room r ON pm.manager_id = r.manager_id
        JOIN lease l ON r.room_id = l.room_id
        JOIN transactions tr ON l.lease_id = tr.lease_id
        GROUP BY pm.manager_id
        ORDER BY total_collected DESC;
    """
    cursor.execute(query)
    report = cursor.fetchall()
    return render_template('report_manager_performance.html', report=report)


# Run App
if __name__ == '__main__':
    app.run(debug=True)
