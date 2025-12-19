"""
销售管理模块路由
包括：销售登记、销售退货、财务统计
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Sales, SalesReturn, FinanceStat, DrugInfo, CustomerInfo, EmployeeInfo, Inventory
from datetime import datetime, timedelta
from sqlalchemy import func, extract

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

# ==================== 销售登记 ====================
@sales_bp.route('/sales')
def sales_list():
    """销售列表"""
    sales_list = db.session.query(Sales, DrugInfo.name, CustomerInfo.name, EmployeeInfo.name).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        join(CustomerInfo, Sales.customer_id == CustomerInfo.customer_id).\
        join(EmployeeInfo, Sales.employee_id == EmployeeInfo.employee_id).\
        order_by(Sales.sales_date.desc()).all()
    return render_template('sales/sales_list.html', sales_list=sales_list)

@sales_bp.route('/sales/add', methods=['GET', 'POST'])
def sales_add():
    """添加销售"""
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        
        sale = Sales(
            drug_id=request.form['drug_id'],
            customer_id=request.form['customer_id'],
            quantity=quantity,
            unit_price=unit_price,
            total_price=quantity * unit_price,
            sales_date=datetime.strptime(request.form['sales_date'], '%Y-%m-%d').date(),
            employee_id=request.form.get('employee_id', 1)
        )
        db.session.add(sale)
        
        # 减少库存
        inventory = Inventory.query.filter_by(
            drug_id=sale.drug_id,
            warehouse_id=request.form.get('warehouse_id', 1)
        ).first()
        if inventory:
            if inventory.quantity >= quantity:
                inventory.quantity -= quantity
            else:
                flash('库存不足！', 'danger')
                return redirect(url_for('sales.sales_add'))
        else:
            flash('该药品无库存！', 'danger')
            return redirect(url_for('sales.sales_add'))
        
        db.session.commit()
        flash('销售登记成功！', 'success')
        return redirect(url_for('sales.sales_list'))
    
    drugs = DrugInfo.query.filter_by(status='在售').all()
    customers = CustomerInfo.query.all()
    return render_template('sales/sales_form.html', drugs=drugs, customers=customers)

# ==================== 销售退货 ====================
@sales_bp.route('/return')
def return_list():
    """销售退货列表"""
    returns = db.session.query(SalesReturn, Sales, DrugInfo.name, EmployeeInfo.name).\
        join(Sales, SalesReturn.sales_id == Sales.sales_id).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        join(EmployeeInfo, SalesReturn.employee_id == EmployeeInfo.employee_id).all()
    return render_template('sales/return_list.html', returns=returns)

@sales_bp.route('/return/add', methods=['GET', 'POST'])
def return_add():
    """添加销售退货"""
    if request.method == 'POST':
        sales_return = SalesReturn(
            sales_id=request.form['sales_id'],
            quantity=request.form['quantity'],
            reason=request.form.get('reason'),
            return_date=datetime.strptime(request.form['return_date'], '%Y-%m-%d').date(),
            employee_id=request.form.get('employee_id', 1)
        )
        db.session.add(sales_return)
        
        # 增加库存
        sale = Sales.query.get(sales_return.sales_id)
        inventory = Inventory.query.filter_by(
            drug_id=sale.drug_id,
            warehouse_id=request.form.get('warehouse_id', 1)
        ).first()
        if inventory:
            inventory.quantity += int(request.form['quantity'])
        
        db.session.commit()
        flash('销售退货处理成功！', 'success')
        return redirect(url_for('sales.return_list'))
    
    sales_records = Sales.query.order_by(Sales.sales_date.desc()).limit(100).all()
    return render_template('sales/return_form.html', sales_records=sales_records)

# ==================== 财务统计 ====================
@sales_bp.route('/finance')
def finance_list():
    """财务统计列表"""
    stats = db.session.query(FinanceStat, EmployeeInfo.name).\
        join(EmployeeInfo, FinanceStat.employee_id == EmployeeInfo.employee_id).\
        order_by(FinanceStat.stat_date.desc()).all()
    return render_template('sales/finance_list.html', stats=stats)

@sales_bp.route('/finance/generate', methods=['POST'])
def finance_generate():
    """生成财务统计"""
    stat_type = request.form['stat_type']
    stat_date = datetime.strptime(request.form['stat_date'], '%Y-%m-%d').date()
    
    # 计算销售总额
    if stat_type == '日':
        total_sales = db.session.query(func.sum(Sales.total_price)).\
            filter(Sales.sales_date == stat_date).scalar() or 0
    else:  # 月
        total_sales = db.session.query(func.sum(Sales.total_price)).\
            filter(extract('year', Sales.sales_date) == stat_date.year).\
            filter(extract('month', Sales.sales_date) == stat_date.month).scalar() or 0
    
    # 计算成本（这里简化处理，实际应从采购价计算）
    total_cost = total_sales * 0.6  # 假设成本率60%
    total_profit = total_sales - total_cost
    
    finance_stat = FinanceStat(
        stat_type=stat_type,
        stat_date=stat_date,
        total_sales=total_sales,
        total_cost=total_cost,
        total_profit=total_profit,
        employee_id=request.form.get('employee_id', 1)
    )
    db.session.add(finance_stat)
    db.session.commit()
    
    flash('财务统计生成成功！', 'success')
    return redirect(url_for('sales.finance_list'))

# ==================== 销售报表 ====================
@sales_bp.route('/report/week')
def report_week():
    """最近一周销售情况"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    # 按日期统计
    daily_sales = db.session.query(
        Sales.sales_date,
        func.sum(Sales.total_price).label('total')
    ).filter(Sales.sales_date.between(start_date, end_date)).\
        group_by(Sales.sales_date).all()
    
    # 按药品统计
    drug_sales = db.session.query(
        DrugInfo.name,
        func.sum(Sales.quantity).label('quantity'),
        func.sum(Sales.total_price).label('total')
    ).join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        filter(Sales.sales_date.between(start_date, end_date)).\
        group_by(DrugInfo.name).\
        order_by(func.sum(Sales.total_price).desc()).all()
    
    return render_template('sales/report_week.html', 
                         daily_sales=daily_sales, 
                         drug_sales=drug_sales,
                         start_date=start_date,
                         end_date=end_date)

@sales_bp.route('/report/top')
def report_top():
    """药品销售排行"""
    top_drugs = db.session.query(
        DrugInfo.name,
        func.sum(Sales.quantity).label('quantity'),
        func.sum(Sales.total_price).label('total')
    ).join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        group_by(DrugInfo.name).\
        order_by(func.sum(Sales.total_price).desc()).\
        limit(20).all()
    
    return render_template('sales/report_top.html', top_drugs=top_drugs)
