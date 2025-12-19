from flask import Flask, session
from flask_migrate import Migrate
from models import db, EmployeeInfo
from routes.dashboard import dashboard_bp
from routes.basic_info import basic_bp
from routes.inventory_mgmt import inventory_bp
from routes.sales_mgmt import sales_bp

from routes.sys_test import api_test_bp
from routes.auth import auth_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medicine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# 配置资源限制
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大请求体16MB
app.config['JSON_SORT_KEYS'] = False

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

app.register_blueprint(api_test_bp)
app.register_blueprint(auth_bp)

from models import init_basic_tables

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_basic_tables()
    app.run(debug=True)
