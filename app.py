from flask import Flask, render_template, jsonify, request
import sqlite3
from config import Config
from modules.bin_monitor import check_bin_levels
from modules.route_optimizer import optimize_routes
from modules.alert_system import process_alerts, check_budget_alert
from modules.ai_predictor import predict_overflow_time
from modules.report_generator import generate_pdf_report
import json

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/routes')
def routes_page():
    return render_template('routes.html')

@app.route('/api/bins')
def api_bins():
    conn = get_db_connection()
    bins = conn.execute('SELECT * FROM Bins').fetchall()
    conn.close()
    bins_list = []
    for ix in bins:
        b_dict = dict(ix)
        b_dict['time_to_full'] = predict_overflow_time(b_dict['fill_level'])
        bins_list.append(b_dict)
        
    return jsonify(bins_list)

@app.route('/api/update_bin', methods=['POST'])
def update_bin():
    data = request.json
    bin_id = data.get('id')
    fill_level = data.get('fill_level')
    
    if bin_id is None or fill_level is None:
        return jsonify({'error': 'Invalid data'}), 400
        
    conn = get_db_connection()
    conn.execute('UPDATE Bins SET fill_level = ? WHERE id = ?', (fill_level, bin_id))
    conn.commit()
    conn.close()
    
    # Process potential alerts
    process_alerts(bin_id, fill_level)
    
    return jsonify({'success': True})

@app.route('/api/optimize')
def api_optimize():
    conn = get_db_connection()
    bins = conn.execute('SELECT * FROM Bins').fetchall()
    conn.close()
    bins_data = [dict(ix) for ix in bins]
    optimized_route, route_coords, cost_metrics = optimize_routes(bins_data)
    
    if cost_metrics is not None:
        # Save to RouteLogs
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO RouteLogs (route_path, distance, fuel_used, fuel_cost, driver_cost, total_cost, efficiency)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            json.dumps(optimized_route),
            cost_metrics['distance_km'],
            cost_metrics['fuel_used'],
            cost_metrics['fuel_cost'],
            cost_metrics['driver_cost'],
            cost_metrics['total_cost'],
            cost_metrics['efficiency']
        ))
        
        # Check if total monthly budget exceeds 85%
        total_spent = conn.execute('SELECT SUM(total_cost) FROM RouteLogs').fetchone()[0] or 0
        budget_limit = conn.execute('SELECT monthly_budget_limit FROM BudgetConfig').fetchone()[0] or 5000000.0
        check_budget_alert(total_spent, budget_limit)
        
        conn.commit()
        conn.close()
    
    return jsonify({
        'route': optimized_route,
        'coordinates': route_coords,
        'costs': cost_metrics
    })

@app.route('/api/budget')
def api_budget():
    conn = get_db_connection()
    config = conn.execute('SELECT * FROM BudgetConfig LIMIT 1').fetchone()
    
    if config:
        config = dict(config)
    else:
        config = {'monthly_budget_limit': 5000000.0}
        
    totals = conn.execute('''
        SELECT 
            SUM(fuel_cost) as total_fuel,
            SUM(driver_cost) as total_driver,
            SUM(total_cost) as total_spent
        FROM RouteLogs
    ''').fetchone()
    
    conn.close()
    
    total_fuel = totals['total_fuel'] or 0.0
    total_driver = totals['total_driver'] or 0.0
    total_spent = totals['total_spent'] or 0.0
    
    return jsonify({
        'limit': config.get('monthly_budget_limit', 5000000.0),
        'total_spent': total_spent,
        'total_fuel': total_fuel,
        'total_driver': total_driver,
        'remaining': config.get('monthly_budget_limit', 5000000.0) - total_spent
    })

@app.route('/api/report')
def api_report():
    conn = get_db_connection()
    bins = conn.execute('SELECT * FROM Bins').fetchall()
    config = conn.execute('SELECT * FROM BudgetConfig LIMIT 1').fetchone()
    totals = conn.execute('''
        SELECT 
            SUM(fuel_cost) as total_fuel,
            SUM(driver_cost) as total_driver,
            SUM(total_cost) as total_spent
        FROM RouteLogs
    ''').fetchone()
    conn.close()
    
    bins_data = [dict(ix) for ix in bins]
    
    budget_data = {
        'limit': dict(config).get('monthly_budget_limit', 5000000.0) if config else 5000000.0,
        'total_fuel': totals['total_fuel'] or 0.0,
        'total_driver': totals['total_driver'] or 0.0,
        'total_spent': totals['total_spent'] or 0.0
    }
    
    import os
    reports_dir = os.path.join(os.path.dirname(__file__), 'static', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, 'monthly_report.pdf')
    
    generate_pdf_report(bins_data, budget_data, report_path)
    
    return jsonify({'report_url': '/static/reports/monthly_report.pdf'})

if __name__ == '__main__':
    app.run(debug=True)
