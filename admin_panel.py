"""
Flask-based web admin panel for bot management - Enhanced 2026 Edition.
Includes support ticket management, agent management, and analytics with Chart.js.
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, send_file
import aiosqlite
import asyncio
import configparser
from functools import wraps
from datetime import datetime, timedelta
import os
import zipfile
import tempfile

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
        async with db.execute('SELECT * FROM users ORDER BY created_at DESC LIMIT 100') as cursor:
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
        
        # Open tickets
        async with db.execute('SELECT COUNT(*) FROM support_tickets WHERE status != "resolved"') as cursor:
            open_tickets = (await cursor.fetchone())[0]
        
        # Total agents
        async with db.execute('SELECT COUNT(*) FROM agents') as cursor:
            total_agents = (await cursor.fetchone())[0]
        
        # Online agents
        async with db.execute('SELECT COUNT(*) FROM agents WHERE is_online = 1') as cursor:
            online_agents = (await cursor.fetchone())[0]
        
        return {
            'total_users': total_users,
            'premium_users': premium_users,
            'banned_users': banned_users,
            'today_requests': today_requests,
            'pending_payments': pending_payments,
            'open_tickets': open_tickets,
            'total_agents': total_agents,
            'online_agents': online_agents,
        }


async def get_chart_data():
    """Get data for analytics charts."""
    async with aiosqlite.connect(DB_PATH) as db:
        # User growth over last 7 days
        user_growth = []
        for i in range(7, 0, -1):
            date = (datetime.now() - timedelta(days=i)).date()
            async with db.execute(
                'SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?', (date,)
            ) as cursor:
                count = (await cursor.fetchone())[0]
                user_growth.append({'date': str(date), 'count': count})
        
        # Requests over last 7 days
        request_stats = []
        for i in range(7, 0, -1):
            date = (datetime.now() - timedelta(days=i)).date()
            async with db.execute(
                'SELECT SUM(count) FROM usage WHERE date = ?', (date,)
            ) as cursor:
                row = await cursor.fetchone()
                count = row[0] if row[0] else 0
                request_stats.append({'date': str(date), 'count': count})
        
        return {
            'user_growth': user_growth,
            'request_stats': request_stats,
        }


async def get_tickets():
    """Get all support tickets."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT * FROM support_tickets 
            ORDER BY created_at DESC 
            LIMIT 50
        ''') as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_agents():
    """Get all agents."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM agents ORDER BY created_at DESC') as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def toggle_premium(user_id):
    """Toggle premium status for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT is_premium FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                new_status = 0 if row[0] else 1
                await db.execute('UPDATE users SET is_premium = ? WHERE user_id = ?', (new_status, user_id))
                await db.commit()


async def toggle_ban(user_id):
    """Toggle ban status for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT is_banned FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                new_status = 0 if row[0] else 1
                await db.execute('UPDATE users SET is_banned = ? WHERE user_id = ?', (new_status, user_id))
                await db.commit()


async def update_ticket_status(ticket_id, status):
    """Update ticket status."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE support_tickets SET status = ? WHERE ticket_id = ?',
            (status, ticket_id)
        )
        await db.commit()


async def get_ticket_attachments(ticket_id):
    """Get attachments for a ticket."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM support_attachments WHERE ticket_id = ?',
            (ticket_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_settings():
    """Get all bot settings."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM bot_settings') as cursor:
            rows = await cursor.fetchall()
            return {row['key']: row['value'] for row in rows}


async def update_setting(key, value):
    """Update a bot setting."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR REPLACE INTO bot_settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)',
            (key, value)
        )
        await db.commit()


# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; justify-content: center; align-items: center; height: 100vh; }
        .login-box { background: white; padding: 50px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 350px; }
        h2 { margin-bottom: 30px; color: #333; text-align: center; }
        input { width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; transition: border 0.3s; }
        input:focus { outline: none; border-color: #667eea; }
        button { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 10px; transition: transform 0.2s; }
        button:hover { transform: translateY(-2px); }
        .error { color: #e74c3c; font-size: 14px; margin-top: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🔐 Admin Panel</h2>
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
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 40px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header h1 { font-size: 24px; }
        .logout { padding: 10px 25px; background: rgba(255,255,255,0.2); color: white; text-decoration: none; border-radius: 8px; transition: background 0.3s; }
        .logout:hover { background: rgba(255,255,255,0.3); }
        .nav { background: white; padding: 15px 40px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 30px; }
        .nav a { display: inline-block; padding: 10px 20px; margin-right: 10px; color: #333; text-decoration: none; border-radius: 8px; transition: background 0.3s; }
        .nav a:hover, .nav a.active { background: #667eea; color: white; }
        .container { padding: 0 40px 40px 40px; max-width: 1400px; margin: 0 auto; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-box { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s; }
        .stat-box:hover { transform: translateY(-5px); }
        .stat-box h3 { font-size: 14px; color: #666; margin-bottom: 10px; }
        .stat-box .number { font-size: 36px; font-weight: bold; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .chart-box { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .chart-box h3 { margin-bottom: 20px; color: #333; }
        .content-box { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid #e0e0e0; }
        th { background: #f8f9fa; font-weight: 600; color: #333; }
        tr:hover { background: #f8f9fa; }
        .btn { padding: 8px 16px; margin: 2px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; font-size: 12px; transition: opacity 0.3s; }
        .btn:hover { opacity: 0.8; }
        .btn-premium { background: #ffc107; color: #333; }
        .btn-ban { background: #e74c3c; color: white; }
        .btn-active { background: #27ae60; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-info { background: #3498db; color: white; }
        .badge { padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }
        .badge-premium { background: #ffc107; color: #333; }
        .badge-banned { background: #e74c3c; color: white; }
        .badge-online { background: #27ae60; color: white; }
        .badge-offline { background: #95a5a6; color: white; }
        .badge-open { background: #3498db; color: white; }
        .badge-closed { background: #27ae60; color: white; }
        .badge-resolved { background: #95a5a6; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Admin Dashboard - YouTube Thumbnail Bot</h1>
        <a href="{{ url_for('logout') }}" class="logout">Logout</a>
    </div>
    
    <div class="nav">
        <a href="{{ url_for('dashboard') }}" class="active">Dashboard</a>
        <a href="{{ url_for('users_page') }}">Users</a>
        <a href="{{ url_for('tickets_page') }}">Support Tickets</a>
        <a href="{{ url_for('agents_page') }}">Agents</a>
        <a href="{{ url_for('settings_page') }}">Settings</a>
    </div>
    
    <div class="container">
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
                <h3>Today's Requests</h3>
                <div class="number">{{ stats.today_requests }}</div>
            </div>
            <div class="stat-box">
                <h3>Open Tickets</h3>
                <div class="number">{{ stats.open_tickets }}</div>
            </div>
            <div class="stat-box">
                <h3>Online Agents</h3>
                <div class="number">{{ stats.online_agents }}/{{ stats.total_agents }}</div>
            </div>
            <div class="stat-box">
                <h3>Pending Payments</h3>
                <div class="number">{{ stats.pending_payments }}</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-box">
                <h3>User Growth (Last 7 Days)</h3>
                <canvas id="userGrowthChart"></canvas>
            </div>
            <div class="chart-box">
                <h3>Daily Requests (Last 7 Days)</h3>
                <canvas id="requestsChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        // User Growth Chart
        const userGrowthCtx = document.getElementById('userGrowthChart').getContext('2d');
        new Chart(userGrowthCtx, {
            type: 'line',
            data: {
                labels: {{ chart_data.user_growth | map(attribute='date') | list | tojson }},
                datasets: [{
                    label: 'New Users',
                    data: {{ chart_data.user_growth | map(attribute='count') | list | tojson }},
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
        
        // Requests Chart
        const requestsCtx = document.getElementById('requestsChart').getContext('2d');
        new Chart(requestsCtx, {
            type: 'bar',
            data: {
                labels: {{ chart_data.request_stats | map(attribute='date') | list | tojson }},
                datasets: [{
                    label: 'Requests',
                    data: {{ chart_data.request_stats | map(attribute='count') | list | tojson }},
                    backgroundColor: '#764ba2'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    </script>
</body>
</html>
'''

USERS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Users Management</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 40px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header h1 { font-size: 24px; }
        .logout { padding: 10px 25px; background: rgba(255,255,255,0.2); color: white; text-decoration: none; border-radius: 8px; transition: background 0.3s; }
        .logout:hover { background: rgba(255,255,255,0.3); }
        .nav { background: white; padding: 15px 40px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 30px; }
        .nav a { display: inline-block; padding: 10px 20px; margin-right: 10px; color: #333; text-decoration: none; border-radius: 8px; transition: background 0.3s; }
        .nav a:hover, .nav a.active { background: #667eea; color: white; }
        .container { padding: 0 40px 40px 40px; max-width: 1400px; margin: 0 auto; }
        .content-box { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid #e0e0e0; }
        th { background: #f8f9fa; font-weight: 600; color: #333; }
        tr:hover { background: #f8f9fa; }
        .btn { padding: 8px 16px; margin: 2px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; font-size: 12px; transition: opacity 0.3s; }
        .btn:hover { opacity: 0.8; }
        .btn-premium { background: #ffc107; color: #333; }
        .btn-ban { background: #e74c3c; color: white; }
        .btn-active { background: #27ae60; color: white; }
        .badge { padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }
        .badge-premium { background: #ffc107; color: #333; }
        .badge-banned { background: #e74c3c; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>👥 Users Management</h1>
        <a href="{{ url_for('logout') }}" class="logout">Logout</a>
    </div>
    
    <div class="nav">
        <a href="{{ url_for('dashboard') }}">Dashboard</a>
        <a href="{{ url_for('users_page') }}" class="active">Users</a>
        <a href="{{ url_for('tickets_page') }}">Support Tickets</a>
        <a href="{{ url_for('agents_page') }}">Agents</a>
        <a href="{{ url_for('settings_page') }}">Settings</a>
    </div>
    
    <div class="container">
        <div class="content-box">
            <h2 style="margin-bottom: 20px;">User List (Latest 100)</h2>
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
                            <a href="{{ url_for('toggle_premium_route', user_id=user.user_id) }}" class="btn btn-premium">
                                {{ 'Remove Premium' if user.is_premium else 'Make Premium' }}
                            </a>
                            <a href="{{ url_for('toggle_ban_route', user_id=user.user_id) }}" class="btn {{ 'btn-active' if user.is_banned else 'btn-ban' }}">
                                {{ 'Unban' if user.is_banned else 'Ban' }}
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
'''

TICKETS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Support Tickets</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 40px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header h1 { font-size: 24px; }
        .logout { padding: 10px 25px; background: rgba(255,255,255,0.2); color: white; text-decoration: none; border-radius: 8px; transition: background 0.3s; }
        .logout:hover { background: rgba(255,255,255,0.3); }
        .nav { background: white; padding: 15px 40px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 30px; }
        .nav a { display: inline-block; padding: 10px 20px; margin-right: 10px; color: #333; text-decoration: none; border-radius: 8px; transition: background 0.3s; }
        .nav a:hover, .nav a.active { background: #667eea; color: white; }
        .container { padding: 0 40px 40px 40px; max-width: 1400px; margin: 0 auto; }
        .content-box { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid #e0e0e0; }
        th { background: #f8f9fa; font-weight: 600; color: #333; }
        tr:hover { background: #f8f9fa; }
        .btn { padding: 8px 16px; margin: 2px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; font-size: 12px; transition: opacity 0.3s; }
        .btn:hover { opacity: 0.8; }
        .btn-success { background: #27ae60; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-info { background: #3498db; color: white; }
        .badge { padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }
        .badge-open { background: #3498db; color: white; }
        .badge-resolved { background: #27ae60; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎫 Support Tickets</h1>
        <a href="{{ url_for('logout') }}" class="logout">Logout</a>
    </div>
    
    <div class="nav">
        <a href="{{ url_for('dashboard') }}">Dashboard</a>
        <a href="{{ url_for('users_page') }}">Users</a>
        <a href="{{ url_for('tickets_page') }}" class="active">Support Tickets</a>
        <a href="{{ url_for('agents_page') }}">Agents</a>
        <a href="{{ url_for('settings_page') }}">Settings</a>
    </div>
    
    <div class="container">
        <div class="content-box">
            <h2 style="margin-bottom: 20px;">Support Tickets (Latest 50)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Ticket ID</th>
                        <th>User ID</th>
                        <th>Subject</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for ticket in tickets %}
                    <tr>
                        <td>{{ ticket.ticket_id }}</td>
                        <td>{{ ticket.user_id }}</td>
                        <td>{{ ticket.subject }}</td>
                        <td>
                            <span class="badge badge-{{ 'resolved' if ticket.status == 'resolved' else 'open' }}">
                                {{ ticket.status }}
                            </span>
                        </td>
                        <td>{{ ticket.priority }}</td>
                        <td>{{ ticket.created_at[:16] }}</td>
                        <td>
                            <a href="{{ url_for('update_ticket_status_route', ticket_id=ticket.ticket_id, status='resolved') }}" 
                               class="btn btn-success">Resolve</a>
                            <a href="{{ url_for('download_attachments', ticket_id=ticket.ticket_id) }}" 
                               class="btn btn-info" title="Download attachment metadata and file IDs">Info ZIP</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
'''

AGENTS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Agent Management</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 40px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header h1 { font-size: 24px; }
        .logout { padding: 10px 25px; background: rgba(255,255,255,0.2); color: white; text-decoration: none; border-radius: 8px; transition: background 0.3s; }
        .logout:hover { background: rgba(255,255,255,0.3); }
        .nav { background: white; padding: 15px 40px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 30px; }
        .nav a { display: inline-block; padding: 10px 20px; margin-right: 10px; color: #333; text-decoration: none; border-radius: 8px; transition: background 0.3s; }
        .nav a:hover, .nav a.active { background: #667eea; color: white; }
        .container { padding: 0 40px 40px 40px; max-width: 1400px; margin: 0 auto; }
        .content-box { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid #e0e0e0; }
        th { background: #f8f9fa; font-weight: 600; color: #333; }
        tr:hover { background: #f8f9fa; }
        .badge { padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }
        .badge-online { background: #27ae60; color: white; }
        .badge-offline { background: #95a5a6; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>👨‍💼 Agent Management</h1>
        <a href="{{ url_for('logout') }}" class="logout">Logout</a>
    </div>
    
    <div class="nav">
        <a href="{{ url_for('dashboard') }}">Dashboard</a>
        <a href="{{ url_for('users_page') }}">Users</a>
        <a href="{{ url_for('tickets_page') }}">Support Tickets</a>
        <a href="{{ url_for('agents_page') }}" class="active">Agents</a>
        <a href="{{ url_for('settings_page') }}">Settings</a>
    </div>
    
    <div class="container">
        <div class="content-box">
            <h2 style="margin-bottom: 20px;">Agent Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Assigned</th>
                        <th>Total Handled</th>
                        <th>Closed</th>
                        <th>Avg Reply Time</th>
                    </tr>
                </thead>
                <tbody>
                    {% for agent in agents %}
                    <tr>
                        <td>{{ agent.user_id }}</td>
                        <td>{{ agent.role }}</td>
                        <td>
                            <span class="badge badge-{{ 'online' if agent.is_online else 'offline' }}">
                                {{ 'Online' if agent.is_online else 'Offline' }}
                            </span>
                        </td>
                        <td>{{ agent.assigned_tickets }}</td>
                        <td>{{ agent.total_tickets_handled }}</td>
                        <td>{{ agent.total_tickets_closed }}</td>
                        <td>{{ agent.avg_reply_time }}s</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
'''

SETTINGS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bot Settings</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 40px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header h1 { font-size: 24px; }
        .logout { padding: 10px 25px; background: rgba(255,255,255,0.2); color: white; text-decoration: none; border-radius: 8px; transition: background 0.3s; }
        .logout:hover { background: rgba(255,255,255,0.3); }
        .nav { background: white; padding: 15px 40px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 30px; }
        .nav a { display: inline-block; padding: 10px 20px; margin-right: 10px; color: #333; text-decoration: none; border-radius: 8px; transition: background 0.3s; }
        .nav a:hover, .nav a.active { background: #667eea; color: white; }
        .container { padding: 0 40px 40px 40px; max-width: 1400px; margin: 0 auto; }
        .content-box { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px; }
        .setting-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #e0e0e0; }
        .setting-row:last-child { border-bottom: none; }
        .setting-label { font-weight: 600; color: #333; }
        .setting-value { color: #666; }
        input[type="text"], input[type="number"] { padding: 10px; border: 2px solid #e0e0e0; border-radius: 6px; width: 200px; }
        button { padding: 10px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 6px; cursor: pointer; }
        button:hover { opacity: 0.9; }
        .toggle { position: relative; display: inline-block; width: 60px; height: 30px; }
        .toggle input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 30px; }
        .slider:before { position: absolute; content: ""; height: 22px; width: 22px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: #667eea; }
        input:checked + .slider:before { transform: translateX(30px); }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚙️ Bot Settings</h1>
        <a href="{{ url_for('logout') }}" class="logout">Logout</a>
    </div>
    
    <div class="nav">
        <a href="{{ url_for('dashboard') }}">Dashboard</a>
        <a href="{{ url_for('users_page') }}">Users</a>
        <a href="{{ url_for('tickets_page') }}">Support Tickets</a>
        <a href="{{ url_for('agents_page') }}">Agents</a>
        <a href="{{ url_for('settings_page') }}" class="active">Settings</a>
    </div>
    
    <div class="container">
        <div class="content-box">
            <h2 style="margin-bottom: 20px;">General Settings</h2>
            
            <form method="POST">
                <div class="setting-row">
                    <div class="setting-label">Maintenance Mode</div>
                    <label class="toggle">
                        <input type="checkbox" name="maintenance_mode" value="1" 
                            {% if settings.maintenance_mode == '1' %}checked{% endif %}>
                        <span class="slider"></span>
                    </label>
                </div>
                
                <div class="setting-row">
                    <div class="setting-label">Force Join Channel</div>
                    <label class="toggle">
                        <input type="checkbox" name="force_join_enabled" value="1"
                            {% if settings.force_join_enabled == '1' %}checked{% endif %}>
                        <span class="slider"></span>
                    </label>
                </div>
                
                <div class="setting-row">
                    <div class="setting-label">Force Join Channel ID</div>
                    <input type="text" name="force_join_channel" 
                        value="{{ settings.force_join_channel or '' }}" 
                        placeholder="@channel_username">
                </div>
                
                <div class="setting-row">
                    <div class="setting-label">Free User Limit</div>
                    <input type="number" name="free_limit" 
                        value="{{ settings.free_limit or '10' }}">
                </div>
                
                <div class="setting-row">
                    <div class="setting-label">Premium User Limit</div>
                    <input type="number" name="premium_limit" 
                        value="{{ settings.premium_limit or '1000' }}">
                </div>
                
                <div class="setting-row">
                    <div class="setting-label">Referral Bonus</div>
                    <input type="number" name="referral_bonus" 
                        value="{{ settings.referral_bonus or '5' }}">
                </div>
                
                <div class="setting-row">
                    <div class="setting-label">Flood Control (seconds)</div>
                    <input type="number" name="flood_time" 
                        value="{{ settings.flood_time or '60' }}">
                </div>
                
                <div style="margin-top: 20px;">
                    <button type="submit">Save Settings</button>
                </div>
            </form>
        </div>
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
    
    stats = loop.run_until_complete(get_stats())
    chart_data = loop.run_until_complete(get_chart_data())
    
    return render_template_string(DASHBOARD_TEMPLATE, stats=stats, chart_data=chart_data)


@app.route('/users')
@login_required
def users_page():
    """Users management page."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    users = loop.run_until_complete(get_users())
    
    return render_template_string(USERS_TEMPLATE, users=users)


@app.route('/tickets')
@login_required
def tickets_page():
    """Support tickets page."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    tickets = loop.run_until_complete(get_tickets())
    
    return render_template_string(TICKETS_TEMPLATE, tickets=tickets)


@app.route('/agents')
@login_required
def agents_page():
    """Agents management page."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    agents = loop.run_until_complete(get_agents())
    
    return render_template_string(AGENTS_TEMPLATE, agents=agents)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
    """Settings page."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if request.method == 'POST':
        # Update settings
        maintenance_mode = '1' if request.form.get('maintenance_mode') else '0'
        force_join_enabled = '1' if request.form.get('force_join_enabled') else '0'
        force_join_channel = request.form.get('force_join_channel', '')
        free_limit = request.form.get('free_limit', '10')
        premium_limit = request.form.get('premium_limit', '1000')
        referral_bonus = request.form.get('referral_bonus', '5')
        flood_time = request.form.get('flood_time', '60')
        
        loop.run_until_complete(update_setting('maintenance_mode', maintenance_mode))
        loop.run_until_complete(update_setting('force_join_enabled', force_join_enabled))
        loop.run_until_complete(update_setting('force_join_channel', force_join_channel))
        loop.run_until_complete(update_setting('free_limit', free_limit))
        loop.run_until_complete(update_setting('premium_limit', premium_limit))
        loop.run_until_complete(update_setting('referral_bonus', referral_bonus))
        loop.run_until_complete(update_setting('flood_time', flood_time))
        
        return redirect(url_for('settings_page'))
    
    settings = loop.run_until_complete(get_settings())
    
    return render_template_string(SETTINGS_TEMPLATE, settings=settings)


@app.route('/toggle_premium/<int:user_id>')
@login_required
def toggle_premium_route(user_id):
    """Toggle premium status."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(toggle_premium(user_id))
    
    return redirect(url_for('users_page'))


@app.route('/toggle_ban/<int:user_id>')
@login_required
def toggle_ban_route(user_id):
    """Toggle ban status."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(toggle_ban(user_id))
    
    return redirect(url_for('users_page'))


@app.route('/update_ticket/<ticket_id>/<status>')
@login_required
def update_ticket_status_route(ticket_id, status):
    """Update ticket status."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(update_ticket_status(ticket_id, status))
    
    return redirect(url_for('tickets_page'))


@app.route('/download_attachments/<ticket_id>')
@login_required
def download_attachments(ticket_id):
    """Download ticket attachments as ZIP."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    attachments = loop.run_until_complete(get_ticket_attachments(ticket_id))
    
    if not attachments:
        return "No attachments found for this ticket.", 404
    
    # Create temp ZIP file with attachment metadata
    # Note: This creates a ZIP with file information, not actual files
    # Actual files are stored in Telegram and can be accessed via bot
    # For full file download, use Telegram Bot API with the file_id
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f'{ticket_id}_attachments_info.zip')
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for i, attachment in enumerate(attachments, 1):
            # Create a text file with attachment info
            info_content = (
                f"Attachment #{i}\n"
                f"{'='*50}\n"
                f"File Type: {attachment['file_type']}\n"
                f"File Name: {attachment.get('file_name', 'N/A')}\n"
                f"Telegram File ID: {attachment['file_id']}\n"
                f"File Unique ID: {attachment['file_unique_id']}\n"
                f"Created: {attachment['created_at']}\n\n"
                f"Note: To download the actual file, use the Telegram Bot API:\n"
                f"https://api.telegram.org/bot<TOKEN>/getFile?file_id={attachment['file_id']}\n"
            )
            filename = f"attachment_{i}_{attachment['file_type']}_info.txt"
            zipf.writestr(filename, info_content)
        
        # Add README
        readme_content = (
            f"Ticket Attachments Information\n"
            f"{'='*50}\n\n"
            f"Ticket ID: {ticket_id}\n"
            f"Total Attachments: {len(attachments)}\n\n"
            f"This ZIP contains metadata about ticket attachments.\n"
            f"Actual files are stored in Telegram and can be accessed via the bot.\n\n"
            f"To download actual files:\n"
            f"1. Use the file_id with Telegram Bot API\n"
            f"2. Or forward files from the bot conversation\n"
        )
        zipf.writestr('README.txt', readme_content)
    
    return send_file(zip_path, as_attachment=True, download_name=f'{ticket_id}_attachments_info.zip')


def main():
    """Run the admin panel."""
    print("🌐 Starting enhanced admin panel on http://localhost:5000")
    print(f"📝 Default credentials: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    print("⚠️  Change these in config.ini!")
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()
