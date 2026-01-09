"""
Flask-based web admin panel for bot management.
Simple, lightweight panel for user management and analytics.
"""

from flask import Flask, render_template_string, request, redirect, url_for, session
import aiosqlite
import asyncio
import configparser
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load config
config = configparser.ConfigParser()
config.read('config.ini')

DB_PATH = config.get('database', 'path', fallback='bot_data.db')
ADMIN_USERNAME = config.get('admin_panel', 'username', fallback='admin')
ADMIN_PASSWORD = config.get('admin_panel', 'password', fallback='admin123')


def login_required(f):
    """Decorator for login required routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


async def get_users():
    """Get all users from database."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users ORDER BY created_at DESC') as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_stats():
    """Get bot statistics."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Total users
        async with db.execute('SELECT COUNT(*) FROM users') as cursor:
            total_users = (await cursor.fetchone())[0]
        
        # Premium users
        async with db.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1') as cursor:
            premium_users = (await cursor.fetchone())[0]
        
        # Banned users
        async with db.execute('SELECT COUNT(*) FROM users WHERE is_banned = 1') as cursor:
            banned_users = (await cursor.fetchone())[0]
        
        # Total requests today
        today = datetime.now().date()
        async with db.execute('SELECT SUM(count) FROM usage WHERE date = ?', (today,)) as cursor:
            row = await cursor.fetchone()
            today_requests = row[0] if row[0] else 0
        
        # Pending payments
        async with db.execute('SELECT COUNT(*) FROM payment_proofs WHERE status = "pending"') as cursor:
            pending_payments = (await cursor.fetchone())[0]
        
        return {
            'total_users': total_users,
            'premium_users': premium_users,
            'banned_users': banned_users,
            'today_requests': today_requests,
            'pending_payments': pending_payments
        }


async def toggle_premium(user_id):
    """Toggle premium status for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Get current status
        async with db.execute('SELECT is_premium FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                new_status = 0 if row[0] else 1
                await db.execute('UPDATE users SET is_premium = ? WHERE user_id = ?', (new_status, user_id))
                await db.commit()


async def toggle_ban(user_id):
    """Toggle ban status for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Get current status
        async with db.execute('SELECT is_banned FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                new_status = 0 if row[0] else 1
                await db.execute('UPDATE users SET is_banned = ? WHERE user_id = ?', (new_status, user_id))
                await db.commit()


# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 300px; }
        h2 { margin-top: 0; color: #333; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .error { color: red; font-size: 14px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🔐 Admin Login</h2>
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .header h1 { margin: 0; color: #333; }
        .logout { float: right; padding: 10px 20px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .stat-box h3 { margin: 0 0 10px 0; color: #666; font-size: 14px; }
        .stat-box .number { font-size: 32px; font-weight: bold; color: #007bff; }
        .users-table { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        .btn { padding: 5px 10px; margin: 2px; border: none; border-radius: 3px; cursor: pointer; text-decoration: none; display: inline-block; font-size: 12px; }
        .btn-premium { background: #ffc107; color: black; }
        .btn-ban { background: #dc3545; color: white; }
        .btn-active { background: #28a745; color: white; }
        .badge { padding: 3px 8px; border-radius: 3px; font-size: 11px; }
        .badge-premium { background: #ffc107; color: black; }
        .badge-banned { background: #dc3545; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <a href="{{ url_for('logout') }}" class="logout">Logout</a>
        <h1>📊 Bot Admin Dashboard</h1>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <h3>Total Users</h3>
            <div class="number">{{ stats.total_users }}</div>
        </div>
        <div class="stat-box">
            <h3>Premium Users</h3>
            <div class="number">{{ stats.premium_users }}</div>
        </div>
        <div class="stat-box">
            <h3>Banned Users</h3>
            <div class="number">{{ stats.banned_users }}</div>
        </div>
        <div class="stat-box">
            <h3>Today's Requests</h3>
            <div class="number">{{ stats.today_requests }}</div>
        </div>
        <div class="stat-box">
            <h3>Pending Payments</h3>
            <div class="number">{{ stats.pending_payments }}</div>
        </div>
    </div>
    
    <div class="users-table">
        <h2>Users</h2>
        <table>
            <thead>
                <tr>
                    <th>User ID</th>
                    <th>Name</th>
                    <th>Username</th>
                    <th>Status</th>
                    <th>Referrals</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user.user_id }}</td>
                    <td>{{ user.first_name or 'N/A' }}</td>
                    <td>@{{ user.username or 'N/A' }}</td>
                    <td>
                        {% if user.is_premium %}
                        <span class="badge badge-premium">Premium</span>
                        {% endif %}
                        {% if user.is_banned %}
                        <span class="badge badge-banned">Banned</span>
                        {% endif %}
                    </td>
                    <td>{{ user.referral_count }}</td>
                    <td>{{ user.created_at[:10] }}</td>
                    <td>
                        <a href="{{ url_for('toggle_premium', user_id=user.user_id) }}" class="btn btn-premium">
                            {{ 'Remove Premium' if user.is_premium else 'Make Premium' }}
                        </a>
                        <a href="{{ url_for('toggle_ban', user_id=user.user_id) }}" class="btn {{ 'btn-active' if user.is_banned else 'btn-ban' }}">
                            {{ 'Unban' if user.is_banned else 'Ban' }}
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error='Invalid credentials')
    
    return render_template_string(LOGIN_TEMPLATE)


@app.route('/logout')
def logout():
    """Logout."""
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    """Main dashboard."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    users = loop.run_until_complete(get_users())
    stats = loop.run_until_complete(get_stats())
    
    return render_template_string(DASHBOARD_TEMPLATE, users=users, stats=stats)


@app.route('/toggle_premium/<int:user_id>')
@login_required
def toggle_premium_route(user_id):
    """Toggle premium status."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(toggle_premium(user_id))
    
    return redirect(url_for('dashboard'))


@app.route('/toggle_ban/<int:user_id>')
@login_required
def toggle_ban_route(user_id):
    """Toggle ban status."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(toggle_ban(user_id))
    
    return redirect(url_for('dashboard'))


def main():
    """Run the admin panel."""
    print("🌐 Starting admin panel on http://localhost:5000")
    print(f"📝 Default credentials: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    print("⚠️  Change these in config.ini!")
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()
