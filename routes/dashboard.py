"""
数据分析和仪表盘模块
"""
from flask import Blueprint, render_template, jsonify, request
from models import db, Sales, DrugInfo, Inventory, FinanceStat, StockIn
from datetime import datetime, timedelta
from sqlalchemy import func, extract

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """仪表盘首页"""
    # 今日销售额
    today = datetime.now().date()
    today_sales = db.session.query(func.sum(Sales.total_price)).\
        filter(Sales.sales_date == today).scalar() or 0
    
    # 本月销售额
    current_month = datetime.now()
    month_sales = db.session.query(func.sum(Sales.total_price)).\
        filter(extract('year', Sales.sales_date) == current_month.year).\
        filter(extract('month', Sales.sales_date) == current_month.month).scalar() or 0
    
    # 库存总数
    total_inventory = db.session.query(func.sum(Inventory.quantity)).scalar() or 0
    
    # 低库存药品数量（低于100）
    low_stock_count = db.session.query(func.count(Inventory.inventory_id)).\
        filter(Inventory.quantity < 100).scalar() or 0
    
    # 药品总数
    total_drugs = db.session.query(func.count(DrugInfo.drug_id)).scalar() or 0
    
    # 最近7天销售趋势
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    daily_sales = db.session.query(
        Sales.sales_date,
        func.sum(Sales.total_price).label('total')
    ).filter(Sales.sales_date.between(start_date, end_date)).\
        group_by(Sales.sales_date).\
        order_by(Sales.sales_date).all()
    
    # 销售Top5药品
    top_drugs = db.session.query(
        DrugInfo.name,
        func.sum(Sales.quantity).label('quantity'),
        func.sum(Sales.total_price).label('total')
    ).join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        filter(Sales.sales_date >= start_date).\
        group_by(DrugInfo.name).\
        order_by(func.sum(Sales.total_price).desc()).\
        limit(5).all()
    
    # 低库存预警
    low_stock_items = db.session.query(Inventory, DrugInfo.name, DrugInfo.unit).\
        join(DrugInfo, Inventory.drug_id == DrugInfo.drug_id).\
        filter(Inventory.quantity < 100).\
        order_by(Inventory.quantity).limit(10).all()
    
    return render_template('dashboard/index.html',
                         today_sales=today_sales,
                         month_sales=month_sales,
                         total_inventory=total_inventory,
                         low_stock_count=low_stock_count,
                         total_drugs=total_drugs,
                         daily_sales=daily_sales,
                         top_drugs=top_drugs,
                         low_stock_items=low_stock_items)

@dashboard_bp.route('/api/sales_trend')
def api_sales_trend():
    """销售趋势API（用于图表）"""
    days = int(request.args.get('days', 30))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    daily_sales = db.session.query(
        Sales.sales_date,
        func.sum(Sales.total_price).label('total'),
        func.count(Sales.sales_id).label('count')
    ).filter(Sales.sales_date.between(start_date, end_date)).\
        group_by(Sales.sales_date).\
        order_by(Sales.sales_date).all()
    
    dates = []
    amounts = []
    counts = []
    
    for sale in daily_sales:
        dates.append(str(sale[0]))
        amounts.append(float(sale[1]))
        counts.append(sale[2])
    
    return jsonify({
        'dates': dates,
        'amounts': amounts,
        'counts': counts
    })

@dashboard_bp.route('/api/inventory_status')
def api_inventory_status():
    """库存状态API"""
    # 库存状态分类：充足(>500), 正常(100-500), 不足(<100)
    abundant = db.session.query(func.count(Inventory.inventory_id)).\
        filter(Inventory.quantity > 500).scalar() or 0
    normal = db.session.query(func.count(Inventory.inventory_id)).\
        filter(Inventory.quantity.between(100, 500)).scalar() or 0
    low = db.session.query(func.count(Inventory.inventory_id)).\
        filter(Inventory.quantity < 100).scalar() or 0
    
    return jsonify({
        'labels': ['充足', '正常', '不足'],
        'data': [abundant, normal, low]
    })

@dashboard_bp.route('/api/top_drugs')
def api_top_drugs():
    """热销药品API"""
    limit = int(request.args.get('limit', 10))
    
    top_drugs = db.session.query(
        DrugInfo.name,
        func.sum(Sales.quantity).label('quantity'),
        func.sum(Sales.total_price).label('total')
    ).join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        group_by(DrugInfo.name).\
        order_by(func.sum(Sales.total_price).desc()).\
        limit(limit).all()
    
    names = []
    quantities = []
    totals = []
    
    for drug in top_drugs:
        names.append(drug[0])
        quantities.append(drug[1])
        totals.append(float(drug[2]))
    
    return jsonify({
        'names': names,
        'quantities': quantities,
        'totals': totals
    })
