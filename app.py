from flask import Flask, session
from flask_migrate import Migrate
from models import db, EmployeeInfo
from config import Config
from routes.dashboard import dashboard_bp
from routes.basic_info import basic_bp
from routes.inventory_mgmt import inventory_bp
from routes.sales_mgmt import sales_bp

from routes.auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

@app.context_processor
def inject_current_employee():
    """向所有模板注入当前登录员工信息"""
    employee = None
    if 'employee_id' in session:
        employee = EmployeeInfo.query.get(session['employee_id'])
    return dict(current_employee=employee)

# 注册蓝图
app.register_blueprint(dashboard_bp)
app.register_blueprint(basic_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(auth_bp)

from models import init_basic_tables

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_basic_tables()
    app.run(debug=True)
