"""
数据分析和仪表盘模块
"""
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from models import (
    db,
    Sales,
    DrugInfo,
    Inventory,
    FinanceStat,
    EmployeeInfo,
    Permission,
    Role,
    RolePermission,
    UserRole,
    SystemLog,
    init_basic_tables,
)
from datetime import datetime
from sqlalchemy import func, extract
import pathlib

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """仪表盘首页"""
    # 今日销售额
    today = datetime.now().date()
    today_sales = db.session.query(func.sum(Sales.quantity * DrugInfo.sale_price)).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        filter(Sales.sales_date == today).scalar() or 0
    
    # 本月销售额
    current_month = datetime.now()
    month_sales = db.session.query(func.sum(Sales.quantity * DrugInfo.sale_price)).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        filter(extract('year', Sales.sales_date) == current_month.year).\
        filter(extract('month', Sales.sales_date) == current_month.month).scalar() or 0
    
    # 库存总数
    total_inventory = db.session.query(func.sum(Inventory.quantity)).scalar() or 0
    
    # 低库存药品数量（低于100）
    low_stock_count = db.session.query(func.count(Inventory.inventory_id)).\
        filter(Inventory.quantity < 100).scalar() or 0
    
    # 药品总数
    total_drugs = db.session.query(func.count(DrugInfo.drug_id)).scalar() or 0
    
    # 低库存预警
    low_stock_items = db.session.query(Inventory, DrugInfo.name, DrugInfo.unit).\
        join(DrugInfo, Inventory.drug_id == DrugInfo.drug_id).\
        filter(Inventory.quantity < 100).\
        order_by(Inventory.quantity).limit(10).all()
    
    # 系统表概览
    permissions = Permission.query.order_by(Permission.permission_id).all()
    roles = Role.query.order_by(Role.role_id).all()
    role_permissions = db.session.query(RolePermission, Role.name, Permission.name).\
        join(Role, RolePermission.role_id == Role.role_id).\
        join(Permission, RolePermission.permission_id == Permission.permission_id).\
        order_by(RolePermission.id).all()
    user_roles = db.session.query(UserRole, EmployeeInfo.name, Role.name).\
        join(EmployeeInfo, UserRole.employee_id == EmployeeInfo.employee_id).\
        join(Role, UserRole.role_id == Role.role_id).\
        order_by(UserRole.id).all()
    logs = SystemLog.query.order_by(SystemLog.action_time.desc()).limit(50).all()

    return render_template('dashboard/index.html',
                         today_sales=today_sales,
                         month_sales=month_sales,
                         total_inventory=total_inventory,
                         low_stock_count=low_stock_count,
                         total_drugs=total_drugs,
                         low_stock_items=low_stock_items,
                         permissions=permissions,
                         roles=roles,
                         role_permissions=role_permissions,
                         user_roles=user_roles,
                         logs=logs)


@dashboard_bp.route('/reset_db', methods=['POST'])
def reset_db():
    """清空并重新初始化数据库，仅保留系统管理员"""
    try:
        # 完整重建所有表，防止外键遗留
        db.session.remove()
        db.drop_all()
        db.create_all()

        # 初始化基础数据（含管理员账号）
        init_basic_tables()

        # 仅保留账号 admin 的系统管理员，删除其他员工
        EmployeeInfo.query.filter(EmployeeInfo.account != 'admin').delete()
        db.session.commit()

        flash('数据库已重建，已恢复基础数据并仅保留系统管理员。', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'数据库重置失败: {e}', 'danger')
    return redirect(url_for('dashboard.index'))
