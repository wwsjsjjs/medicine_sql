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
        warehouse_id = request.form.get('warehouse_id', 1)
        
        # 验证药品是否存在
        drug = DrugInfo.query.get(request.form['drug_id'])
        if not drug:
            flash('指定的药品不存在！', 'danger')
            return redirect(url_for('sales.sales_add'))
        
        # 验证客户是否存在
        customer = CustomerInfo.query.get(request.form['customer_id'])
        if not customer:
            flash('指定的客户不存在，请先添加客户信息！', 'danger')
            return redirect(url_for('sales.sales_add'))
        
        # 验证库存是否存在且足够
        inventory = Inventory.query.filter_by(
            drug_id=request.form['drug_id'],
            warehouse_id=warehouse_id
        ).first()
        if not inventory:
            flash('该药品无库存，无法销售！', 'danger')
            return redirect(url_for('sales.sales_add'))
        if inventory.quantity < quantity:
            flash(f'库存不足！当前库存：{inventory.quantity}，销售数量：{quantity}', 'danger')
            return redirect(url_for('sales.sales_add'))
        
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
        inventory.quantity -= quantity
        
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
        quantity = int(request.form['quantity'])
        warehouse_id = request.form.get('warehouse_id', 1)
        
        # 验证销售记录是否存在
        sale = Sales.query.get(request.form['sales_id'])
        if not sale:
            flash('指定的销售记录不存在！', 'danger')
            return redirect(url_for('sales.return_add'))
        
        # 验证退货数量是否合理
        if quantity > sale.quantity:
            flash(f'退货数量不能超过销售数量！销售数量：{sale.quantity}', 'danger')
            return redirect(url_for('sales.return_add'))
        
        sales_return = SalesReturn(
            sales_id=request.form['sales_id'],
            quantity=quantity,
            reason=request.form.get('reason'),
            return_date=datetime.strptime(request.form['return_date'], '%Y-%m-%d').date(),
            employee_id=request.form.get('employee_id', 1)
        )
        db.session.add(sales_return)
        
        # 增加库存
        inventory = Inventory.query.filter_by(
            drug_id=sale.drug_id,
            warehouse_id=warehouse_id
        ).first()
        if inventory:
            inventory.quantity += quantity
        else:
            # 如果库存记录不存在，创建新记录
            inventory = Inventory(
                drug_id=sale.drug_id,
                warehouse_id=warehouse_id,
                quantity=quantity
            )
            db.session.add(inventory)
        
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
    admin = EmployeeInfo.query.filter_by(account='admin').first()
    employee_id = request.form.get('employee_id') or (admin.employee_id if admin else None)
    
    filters = []
    if stat_type == '日':
        filters.append(Sales.sales_date == stat_date)
    else:  # 月
        filters.append(extract('year', Sales.sales_date) == stat_date.year)
        filters.append(extract('month', Sales.sales_date) == stat_date.month)

    # 销售额与成本（按销售数量 * 进货价统计）
    from decimal import Decimal
    total_sales = db.session.query(func.sum(Sales.total_price)).\
        filter(*filters).scalar() or 0
    total_cost = db.session.query(func.sum(Sales.quantity * DrugInfo.purchase_price)).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        filter(*filters).scalar() or 0

    total_sales = Decimal(str(total_sales)) if total_sales else Decimal('0')
    total_cost = Decimal(str(total_cost)) if total_cost else Decimal('0')
    total_profit = total_sales - total_cost
    
    # 检查是否已存在相同的统计记录
    finance_stat = FinanceStat.query.filter_by(stat_type=stat_type, stat_date=stat_date).first()
    if finance_stat:
        # 已存在则更新
        finance_stat.total_sales = total_sales
        finance_stat.total_cost = total_cost
        finance_stat.total_profit = total_profit
        finance_stat.employee_id = employee_id
        flash('财务统计更新成功！', 'success')
    else:
        # 不存在则插入
        finance_stat = FinanceStat(
            stat_type=stat_type,
            stat_date=stat_date,
            total_sales=total_sales,
            total_cost=total_cost,
            total_profit=total_profit,
            employee_id=employee_id
        )
        db.session.add(finance_stat)
        flash('财务统计生成成功！', 'success')
    
    db.session.commit()
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
