from flask import Flask
from flask_migrate import Migrate
from models import db
from routes.dashboard import dashboard_bp
from routes.basic_info import basic_bp
from routes.inventory_mgmt import inventory_bp
from routes.sales_mgmt import sales_bp
from routes.api_test import api_test_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medicine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# 配置资源限制
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大请求体16MB
app.config['JSON_SORT_KEYS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# 注册蓝图
app.register_blueprint(dashboard_bp)
app.register_blueprint(basic_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(api_test_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
