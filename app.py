from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='sana anitha@1234',
        database='train_booking'
    )

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            cursor.execute("INSERT INTO users (username, password, email, phone) VALUES (%s, %s, %s, %s)",
                           (username, password, email, phone))
            conn.commit()
            flash('User registered successfully!', 'success')
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'danger')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Search Trains
@app.route('/search_trains', methods=['GET', 'POST'])
def search_trains():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']
        travel_date = request.form['travel_date']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM trains WHERE source = %s AND destination = %s AND departure_date = %s
        """, (source, destination, travel_date))
        trains = cursor.fetchall()
        conn.close()
        return render_template('search_trains.html', trains=trains)

    return render_template('search_trains.html', trains=None)

# Book Tickets
@app.route('/book_tickets/<int:train_id>', methods=['GET', 'POST'])
def book_ticket(train_id):
    if 'user_id' not in session:
        flash('Please login to access this page.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        seat_class = request.form['seat_class']
        number_of_seats = int(request.form['number_of_seats'])

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT seats_available FROM trains WHERE train_id = %s", (train_id,))
        available_seats = cursor.fetchone()

        if available_seats and available_seats['seats_available'] >= number_of_seats:
            cursor.execute("""
                UPDATE trains SET seats_available = seats_available - %s WHERE train_id = %s
            """, (number_of_seats, train_id))

            booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payment_status = 'pending'
            cursor.execute("""
                INSERT INTO bookings (user_id, train_id, seat_class, number_of_seats, booking_time, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (session['user_id'], train_id, seat_class, number_of_seats, booking_time, payment_status))
            conn.commit()
            booking_id = cursor.lastrowid
            flash('Booking successful! Proceed to payment.', 'success')
            conn.close()
            return redirect(url_for('make_payment', booking_id=booking_id))
        else:
            flash('Not enough seats available!', 'danger')
        conn.close()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM trains WHERE train_id = %s", (train_id,))
    train = cursor.fetchone()
    conn.close()
    return render_template('book_ticket.html', train=train)

# View Bookings
@app.route('/view_bookings')
def view_bookings():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.booking_id, t.train_name, b.booking_time, b.number_of_seats, b.payment_status
        FROM bookings b
        JOIN trains t ON b.train_id = t.train_id
        WHERE b.user_id = %s
    """, (session['user_id'],))
    bookings = cursor.fetchall()
    conn.close()
    return render_template('view_bookings.html', bookings=bookings)

# Make Payment
@app.route('/make_payment/<int:booking_id>', methods=['GET', 'POST'])
def make_payment(booking_id):
    if 'user_id' not in session:
        flash('Please login to access this page.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET payment_status = 'confirmed' WHERE booking_id = %s", (booking_id,))
        conn.commit()
        conn.close()
        flash('Payment successful!', 'success')
        return redirect(url_for('view_bookings'))

    return render_template('make_payment.html', booking_id=booking_id)


@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session:
        flash('Please login to access this page.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cancellation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE bookings
        SET payment_status = 'cancelled', cancellation_time = %s
        WHERE booking_id = %s
    """, (cancellation_time, booking_id))
    conn.commit()
    conn.close()
    flash('Booking cancelled successfully!', 'success')
    return redirect(url_for('view_bookings'))

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return render_template('logout_confirmation.html')


if __name__ == '__main__':
    app.run(debug=True)
