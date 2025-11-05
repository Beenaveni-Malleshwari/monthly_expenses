    
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response, g
import sqlite3
import csv
from datetime import datetime, timedelta
import os
import json
from io import StringIO

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['DATABASE'] = 'database.db'

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection at the end of request"""
    if hasattr(g, 'db'):
        g.db.close()

def init_db():
    """Initialize database with required tables"""
    db = get_db()
    
    # Create expenses table
    db.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create categories table
    db.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            budget_limit REAL DEFAULT 0,
            color TEXT DEFAULT '#007bff'
        )
    ''')
    
    # Insert default categories
    default_categories = [
        ('Food & Dining', 300, '#FF6384'),
        ('Transportation', 200, '#36A2EB'),
        ('Entertainment', 150, '#FFCE56'),
        ('Shopping', 250, '#4BC0C0'),
        ('Bills & Utilities', 400, '#9966FF'),
        ('Healthcare', 100, '#FF9F40'),
        ('Education', 200, '#FF6384'),
        ('Other', 100, '#C9CBCF')
    ]
    
    for category in default_categories:
        try:
            db.execute(
                'INSERT OR IGNORE INTO categories (name, budget_limit, color) VALUES (?, ?, ?)',
                category
            )
        except:
            pass
    
    db.commit()

# Routes
@app.route('/')
def index():
    """Home page with overview"""
    db = get_db()
    
    # Get recent expenses
    recent_expenses = db.execute('''
        SELECT * FROM expenses 
        ORDER BY date DESC, created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    # Get current month total
    today = datetime.now()
    first_day = today.replace(day=1)
    
    monthly_total = db.execute('''
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM expenses 
        WHERE date BETWEEN ? AND ?
    ''', (first_day.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))).fetchone()['total']
    
    # Get category totals for current month
    category_totals = db.execute('''
        SELECT category, SUM(amount) as total 
        FROM expenses 
        WHERE date BETWEEN ? AND ?
        GROUP BY category 
        ORDER BY total DESC
    ''', (first_day.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))).fetchall()
    
    return render_template('index.html',
                         recent_expenses=recent_expenses,
                         monthly_total=monthly_total,
                         category_totals=category_totals)

@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    """Add new expense"""
    db = get_db()
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            description = request.form['description'].strip()
            category = request.form['category']
            date = request.form.get('date') or datetime.now().strftime('%Y-%m-%d')
            
            if amount <= 0:
                flash('Amount must be greater than 0', 'error')
            else:
                db.execute('''
                    INSERT INTO expenses (amount, description, category, date)
                    VALUES (?, ?, ?, ?)
                ''', (amount, description, category, date))
                db.commit()
                flash('Expense added successfully!', 'success')
                return redirect(url_for('expenses'))
                
        except ValueError:
            flash('Please enter a valid amount', 'error')
        except Exception as e:
            flash(f'Error adding expense: {str(e)}', 'error')
    
    categories = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
    return render_template('add_expense.html', categories=categories)

@app.route('/expenses')
def expenses():
    """View all expenses"""
    db = get_db()
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    
    query = 'SELECT * FROM expenses WHERE 1=1'
    params = []
    
    if search:
        query += ' AND description LIKE ?'
        params.append(f'%{search}%')
    
    if category_filter:
        query += ' AND category = ?'
        params.append(category_filter)
    
    query += ' ORDER BY date DESC, created_at DESC'
    
    # Simple pagination
    limit = 20
    offset = (page - 1) * limit
    query += ' LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    expenses_data = db.execute(query, params).fetchall()
    
    categories = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
    
    return render_template('expenses.html',
                         expenses=expenses_data,
                         categories=categories,
                         current_page=page,
                         search=search,
                         category_filter=category_filter)

@app.route('/edit-expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    """Edit existing expense"""
    db = get_db()
    
    expense = db.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()
    if not expense:
        flash('Expense not found', 'error')
        return redirect(url_for('expenses'))
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            description = request.form['description'].strip()
            category = request.form['category']
            date = request.form['date']
            
            db.execute('''
                UPDATE expenses 
                SET amount = ?, description = ?, category = ?, date = ?
                WHERE id = ?
            ''', (amount, description, category, date, expense_id))
            db.commit()
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('expenses'))
            
        except ValueError:
            flash('Please enter a valid amount', 'error')
        except Exception as e:
            flash(f'Error updating expense: {str(e)}', 'error')
    
    categories = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
    return render_template('edit_expense.html', expense=expense, categories=categories)

@app.route('/delete-expense/<int:expense_id>')
def delete_expense(expense_id):
    """Delete expense"""
    db = get_db()
    
    try:
        db.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        db.commit()
        flash('Expense deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting expense: {str(e)}', 'error')
    
    return redirect(url_for('expenses'))

@app.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    return render_template('dashboard.html')

@app.route('/api/expense-data')
def api_expense_data():
    """API endpoint for chart data"""
    db = get_db()
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        # Default to current month
        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Category-wise spending
    category_data = db.execute('''
        SELECT category, SUM(amount) as total 
        FROM expenses 
        WHERE date BETWEEN ? AND ?
        GROUP BY category 
        ORDER BY total DESC
    ''', (start_date, end_date)).fetchall()
    
    return jsonify({
        'category_data': {
            'labels': [row['category'] for row in category_data],
            'amounts': [row['total'] for row in category_data],
            'colors': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        },
        'total_spent': sum(row['total'] for row in category_data)
    })

@app.route('/categories')
def categories():
    """Manage categories"""
    db = get_db()
    categories_data = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
    return render_template('categories.html', categories=categories_data)

@app.route('/add-category', methods=['POST'])
def add_category():
    """Add new category"""
    db = get_db()
    
    try:
        name = request.form['name'].strip()
        budget_limit = float(request.form.get('budget_limit', 0))
        color = request.form.get('color', '#007bff')
        
        db.execute('''
            INSERT INTO categories (name, budget_limit, color)
            VALUES (?, ?, ?)
        ''', (name, budget_limit, color))
        db.commit()
        flash('Category added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Category name already exists!', 'error')
    except Exception as e:
        flash(f'Error adding category: {str(e)}', 'error')
    
    return redirect(url_for('categories'))

@app.route('/update-category/<int:category_id>', methods=['POST'])
def update_category(category_id):
    """Update category"""
    db = get_db()
    
    try:
        name = request.form['name'].strip()
        budget_limit = float(request.form.get('budget_limit', 0))
        color = request.form.get('color', '#007bff')
        
        db.execute('''
            UPDATE categories 
            SET name = ?, budget_limit = ?, color = ?
            WHERE id = ?
        ''', (name, budget_limit, color, category_id))
        db.commit()
        flash('Category updated successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Category name already exists!', 'error')
    except Exception as e:
        flash(f'Error updating category: {str(e)}', 'error')
    
    return redirect(url_for('categories'))

@app.route('/delete-category/<int:category_id>')
def delete_category(category_id):
    """Delete category"""
    db = get_db()
    
    try:
        # Check if category is used in expenses
        expense_count = db.execute(
            'SELECT COUNT(*) as count FROM expenses WHERE category = (SELECT name FROM categories WHERE id = ?)',
            (category_id,)
        ).fetchone()['count']
        
        if expense_count > 0:
            flash('Cannot delete category that is used in expenses!', 'error')
        else:
            db.execute('DELETE FROM categories WHERE id = ?', (category_id,))
            db.commit()
            flash('Category deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'error')
    
    return redirect(url_for('categories'))

@app.route('/export-expenses')
def export_expenses():
    """Export expenses to CSV without pandas"""
    db = get_db()
    
    try:
        # Get expenses data
        expenses_data = db.execute('''
            SELECT date, amount, description, category 
            FROM expenses 
            ORDER BY date DESC
        ''').fetchall()
        
        # Create CSV using StringIO
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Amount', 'Description', 'Category'])
        
        # Write data rows
        for expense in expenses_data:
            writer.writerow([expense['date'], expense['amount'], expense['description'], expense['category']])
        
        # Get the CSV data
        csv_data = output.getvalue()
        output.close()
        
        # Return as downloadable file
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=expenses_export.csv"}
        )
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('expenses'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    print("🚀 Starting Smart Expense Tracker...")
    print("📊 Database initialized!")
    print("🌐 Server running on: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
