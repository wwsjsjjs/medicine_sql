from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 药品信息表
class DrugInfo(db.Model):
    __tablename__ = 'drug_info'
    drug_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    spec = db.Column(db.String(100))
    manufacturer = db.Column(db.String(200))
    approval_number = db.Column(db.String(100))
    category = db.Column(db.String(50))  # 处方/非处方
    unit = db.Column(db.String(20))
    purchase_price = db.Column(db.Numeric(10, 2))
    sale_price = db.Column(db.Numeric(10, 2))
    expiry_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='在售')
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# 员工信息表
class EmployeeInfo(db.Model):
    __tablename__ = 'employee_info'
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    hire_date = db.Column(db.Date)
    account = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    status = db.Column(db.String(20), default='在职')
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# 客户信息表
class CustomerInfo(db.Model):
    __tablename__ = 'customer_info'
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20))  # 零售/批发
    contact = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# 供应商信息表
class SupplierInfo(db.Model):
    __tablename__ = 'supplier_info'
    supplier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    qualification_no = db.Column(db.String(100))
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# 权限表
class Permission(db.Model):
    __tablename__ = 'permission'
    permission_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

# 角色表
class Role(db.Model):
    __tablename__ = 'role'
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

# 角色权限关联表
class RolePermission(db.Model):
    __tablename__ = 'role_permission'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.permission_id'))

# 用户角色关联表
class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))

# 系统日志表
class SystemLog(db.Model):
    __tablename__ = 'system_log'
    log_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id'))
    action_type = db.Column(db.String(50))
    table_name = db.Column(db.String(100))
    action_time = db.Column(db.DateTime, default=datetime.now)
    action_content = db.Column(db.Text)

# 入库登记表
class StockIn(db.Model):
    __tablename__ = 'stock_in'
    stock_in_id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug_info.drug_id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier_info.supplier_id'))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Numeric(10, 2))
    total_price = db.Column(db.Numeric(10, 2))
    stock_in_date = db.Column(db.Date)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id'))
    remark = db.Column(db.String(200))
    create_time = db.Column(db.DateTime, default=datetime.now)

# 库存表
class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug_info.drug_id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.warehouse_id'))
    quantity = db.Column(db.Integer)
    location = db.Column(db.String(100))
    last_check_date = db.Column(db.Date)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# 仓库表
class Warehouse(db.Model):
    __tablename__ = 'warehouse'
    warehouse_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    manager_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id'))
    create_time = db.Column(db.DateTime, default=datetime.now)

# 库存盘点表
class InventoryCheck(db.Model):
    __tablename__ = 'inventory_check'
    check_id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug_info.drug_id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.warehouse_id'))
    checked_quantity = db.Column(db.Integer)
    actual_quantity = db.Column(db.Integer)
    diff_reason = db.Column(db.String(200))
    check_date = db.Column(db.Date)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id'))
    create_time = db.Column(db.DateTime, default=datetime.now)

# 退货处理表
class ReturnStock(db.Model):
    __tablename__ = 'return_stock'
    return_id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug_info.drug_id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier_info.supplier_id'))
    quantity = db.Column(db.Integer)
    reason = db.Column(db.String(200))
    return_date = db.Column(db.Date)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id'))
    create_time = db.Column(db.DateTime, default=datetime.now)

# 销售登记表
class Sales(db.Model):
    __tablename__ = 'sales'
    sales_id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug_info.drug_id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_info.customer_id'))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Numeric(10, 2))
    total_price = db.Column(db.Numeric(10, 2))
    sales_date = db.Column(db.Date)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id'))
    create_time = db.Column(db.DateTime, default=datetime.now)

# 销售退货表
class SalesReturn(db.Model):
    __tablename__ = 'sales_return'
    sales_return_id = db.Column(db.Integer, primary_key=True)
    sales_id = db.Column(db.Integer, db.ForeignKey('sales.sales_id'))
    quantity = db.Column(db.Integer)
    reason = db.Column(db.String(200))
    return_date = db.Column(db.Date)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id'))
    create_time = db.Column(db.DateTime, default=datetime.now)

# 财务统计表
class FinanceStat(db.Model):
    __tablename__ = 'finance_stat'
    stat_id = db.Column(db.Integer, primary_key=True)
    stat_type = db.Column(db.String(20))  # 日/月
    stat_date = db.Column(db.Date)
    total_sales = db.Column(db.Numeric(15, 2))
    total_cost = db.Column(db.Numeric(15, 2))
    total_profit = db.Column(db.Numeric(15, 2))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id'))
    create_time = db.Column(db.DateTime, default=datetime.now)
