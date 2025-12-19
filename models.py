import json
def log_system_action(employee_id, action_type, table_name, action_content):
    """写入系统日志（employee_id可为None，action_content建议为json字符串）"""
    log = SystemLog(
        employee_id=employee_id,
        action_type=action_type,
        table_name=table_name,
        action_content=json.dumps(action_content, ensure_ascii=False) if not isinstance(action_content, str) else action_content
    )
    db.session.add(log)
    db.session.commit()
def init_basic_tables():
    """初始化基础表数据（角色、权限、角色权限、用户角色、系统管理员）"""
    from sqlalchemy.exc import IntegrityError
    # 1. 初始化权限
    default_permissions = [
        {'name': '系统管理', 'description': '系统管理权限'},
        {'name': '药品管理', 'description': '药品信息管理'},
        {'name': '库存管理', 'description': '库存管理权限'},
        {'name': '销售管理', 'description': '销售管理权限'},
        {'name': '客户管理', 'description': '客户信息管理'},
        {'name': '供应商管理', 'description': '供应商信息管理'},
        {'name': '财务统计', 'description': '财务统计查看'},
    ]
    for perm in default_permissions:
        if not Permission.query.filter_by(name=perm['name']).first():
            db.session.add(Permission(**perm))
            db.session.flush()
            log_system_action(None, 'insert', 'permission', perm)
    db.session.commit()

    # 2. 初始化角色
    default_roles = [
        {'name': '系统管理员', 'description': '拥有全部权限'},
        {'name': '普通员工', 'description': '普通操作权限'},
    ]
    for role in default_roles:
        if not Role.query.filter_by(name=role['name']).first():
            db.session.add(Role(**role))
            db.session.flush()
            log_system_action(None, 'insert', 'role', role)
    db.session.commit()

    # 3. 角色权限分配（系统管理员拥有全部权限，普通员工部分权限）
    admin_role = Role.query.filter_by(name='系统管理员').first()
    employee_role = Role.query.filter_by(name='普通员工').first()
    all_permissions = Permission.query.all()
    for perm in all_permissions:
        if not RolePermission.query.filter_by(role_id=admin_role.role_id, permission_id=perm.permission_id).first():
            db.session.add(RolePermission(role_id=admin_role.role_id, permission_id=perm.permission_id))
            db.session.flush()
            log_system_action(None, 'insert', 'role_permission', {'role_id': admin_role.role_id, 'permission_id': perm.permission_id})
    # 普通员工只分配部分权限
    for perm in all_permissions:
        if perm.name in ['药品管理', '库存管理', '销售管理', '客户管理', '供应商管理']:
            if not RolePermission.query.filter_by(role_id=employee_role.role_id, permission_id=perm.permission_id).first():
                db.session.add(RolePermission(role_id=employee_role.role_id, permission_id=perm.permission_id))
                db.session.flush()
                log_system_action(None, 'insert', 'role_permission', {'role_id': employee_role.role_id, 'permission_id': perm.permission_id})
    db.session.commit()

    # 4. 初始化系统管理员账号
    admin = EmployeeInfo.query.filter_by(account='admin').first()
    if not admin:
        admin = EmployeeInfo(
            name='系统管理员',
            account='admin',
            password='admin123',
            phone='13000000000',
            department='管理',
            position='系统管理员',
            status='在职'
        )
        db.session.add(admin)
        db.session.commit()
        log_system_action(None, 'insert', 'employee_info', {
            'name': '系统管理员',
            'account': 'admin',
            'phone': '13000000000',
            'department': '管理',
            'position': '系统管理员',
            'status': '在职'
        })

    # 5. 管理员分配角色
    if not UserRole.query.filter_by(employee_id=admin.employee_id, role_id=admin_role.role_id).first():
        db.session.add(UserRole(employee_id=admin.employee_id, role_id=admin_role.role_id))
        db.session.commit()
        log_system_action(admin.employee_id, 'insert', 'user_role', {'employee_id': admin.employee_id, 'role_id': admin_role.role_id})

    # 6. 系统日志表可不插入默认数据

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 药品信息表
class DrugInfo(db.Model):
    __tablename__ = 'drug_info'
    drug_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    spec = db.Column(db.String(100))
    manufacturer = db.Column(db.String(200))
    approval_number = db.Column(db.String(100), unique=True)
    category = db.Column(db.String(50))  # 处方/非处方
    unit = db.Column(db.String(20))
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    expiry_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='在售', nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 员工信息表
class EmployeeInfo(db.Model):
    __tablename__ = 'employee_info'
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True)
    hire_date = db.Column(db.Date)
    account = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='在职', nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 客户信息表
class CustomerInfo(db.Model):
    __tablename__ = 'customer_info'
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False)  # 零售/批发
    contact = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True, index=True)
    address = db.Column(db.String(200))
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 供应商信息表
class SupplierInfo(db.Model):
    __tablename__ = 'supplier_info'
    supplier_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    contact = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True, index=True)
    address = db.Column(db.String(200))
    qualification_no = db.Column(db.String(100), unique=True, index=True)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 权限表
class Permission(db.Model):
    __tablename__ = 'permission'
    permission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.String(200))
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 角色表
class Role(db.Model):
    __tablename__ = 'role'
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.String(200))
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 角色权限关联表
class RolePermission(db.Model):
    __tablename__ = 'role_permission'
    __table_args__ = (
        db.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id', ondelete='CASCADE'), nullable=False, index=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.permission_id', ondelete='CASCADE'), nullable=False, index=True)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 用户角色关联表
class UserRole(db.Model):
    __tablename__ = 'user_role'
    __table_args__ = (
        db.UniqueConstraint('employee_id', 'role_id', name='uq_employee_role'),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id', ondelete='CASCADE'), nullable=False, index=True)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 系统日志表
class SystemLog(db.Model):
    __tablename__ = 'system_log'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id', ondelete='SET NULL'), index=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)
    table_name = db.Column(db.String(100), nullable=False, index=True)
    action_time = db.Column(db.DateTime, default=datetime.now, nullable=False, index=True)
    action_content = db.Column(db.Text)

# 入库登记表
class StockIn(db.Model):
    __tablename__ = 'stock_in'
    stock_in_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug_info.drug_id', ondelete='CASCADE'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier_info.supplier_id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_in_date = db.Column(db.Date, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id', ondelete='SET NULL'))
    remark = db.Column(db.String(200))
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 库存表
class Inventory(db.Model):
    __tablename__ = 'inventory'
    __table_args__ = (
        db.UniqueConstraint('drug_id', 'warehouse_id', name='uq_drug_warehouse'),
    )
    inventory_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug_info.drug_id', ondelete='CASCADE'), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.warehouse_id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    location = db.Column(db.String(100))
    last_check_date = db.Column(db.Date)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 仓库表
class Warehouse(db.Model):
    __tablename__ = 'warehouse'
    warehouse_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    address = db.Column(db.String(200))
    manager_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id', ondelete='SET NULL'))
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 库存盘点表
class InventoryCheck(db.Model):
    __tablename__ = 'inventory_check'
    check_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug_info.drug_id', ondelete='CASCADE'), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.warehouse_id', ondelete='CASCADE'), nullable=False, index=True)
    checked_quantity = db.Column(db.Integer, nullable=False)
    actual_quantity = db.Column(db.Integer, nullable=False)
    diff_reason = db.Column(db.String(200))
    check_date = db.Column(db.Date, nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id', ondelete='SET NULL'))
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 退货处理表
class ReturnStock(db.Model):
    __tablename__ = 'return_stock'
    return_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug_info.drug_id', ondelete='CASCADE'), nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier_info.supplier_id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    return_date = db.Column(db.Date, nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id', ondelete='SET NULL'))
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 销售登记表
class Sales(db.Model):
    __tablename__ = 'sales'
    sales_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug_info.drug_id', ondelete='CASCADE'), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_info.customer_id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    sales_date = db.Column(db.Date, nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id', ondelete='SET NULL'))
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 销售退货表
class SalesReturn(db.Model):
    __tablename__ = 'sales_return'
    sales_return_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sales_id = db.Column(db.Integer, db.ForeignKey('sales.sales_id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    return_date = db.Column(db.Date, nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id', ondelete='SET NULL'))
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 财务统计表
class FinanceStat(db.Model):
    __tablename__ = 'finance_stat'
    __table_args__ = (
        db.UniqueConstraint('stat_type', 'stat_date', name='uq_stat_type_date'),
    )
    stat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stat_type = db.Column(db.String(20), nullable=False)  # 日/月
    stat_date = db.Column(db.Date, nullable=False, index=True)
    total_sales = db.Column(db.Numeric(15, 2), default=0, nullable=False)
    total_cost = db.Column(db.Numeric(15, 2), default=0, nullable=False)
    total_profit = db.Column(db.Numeric(15, 2), default=0, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_info.employee_id', ondelete='SET NULL'))
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
