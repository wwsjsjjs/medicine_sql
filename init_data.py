"""
数据初始化脚本 - 生成测试数据
"""
from app import app
from models import db, DrugInfo, EmployeeInfo, CustomerInfo, SupplierInfo, Warehouse, Inventory, Sales, StockIn
from datetime import datetime, timedelta
import random

def init_data():
    with app.app_context():
        # 清空现有数据
        db.drop_all()
        db.create_all()
        
        print("开始生成测试数据...")
        
        # 1. 创建员工
        employees = [
            EmployeeInfo(name='张三', department='销售部', position='销售经理', phone='13800138001', 
                        hire_date=datetime(2020, 1, 1).date(), account='zhangsan', password='123456', status='在职'),
            EmployeeInfo(name='李四', department='仓储部', position='仓管员', phone='13800138002', 
                        hire_date=datetime(2021, 3, 15).date(), account='lisi', password='123456', status='在职'),
            EmployeeInfo(name='王五', department='采购部', position='采购员', phone='13800138003', 
                        hire_date=datetime(2019, 6, 1).date(), account='wangwu', password='123456', status='在职'),
            EmployeeInfo(name='赵六', department='财务部', position='会计', phone='13800138004', 
                        hire_date=datetime(2021, 9, 1).date(), account='zhaoliu', password='123456', status='在职'),
        ]
        db.session.add_all(employees)
        db.session.commit()
        print(f"✓ 创建了 {len(employees)} 个员工")
        
        # 2. 创建供应商
        suppliers = [
            SupplierInfo(name='华康医药有限公司', contact='陈经理', phone='021-12345678', 
                        address='上海市浦东新区', qualification_no='SH20210001'),
            SupplierInfo(name='康源药业集团', contact='刘总', phone='010-87654321', 
                        address='北京市朝阳区', qualification_no='BJ20200002'),
            SupplierInfo(name='健民制药厂', contact='孙主任', phone='0755-98765432', 
                        address='深圳市南山区', qualification_no='SZ20190003'),
        ]
        db.session.add_all(suppliers)
        db.session.commit()
        print(f"✓ 创建了 {len(suppliers)} 个供应商")
        
        # 3. 创建客户
        customers = [
            CustomerInfo(name='仁和大药房', type='批发', contact='周经理', phone='13900139001', address='市中心路100号'),
            CustomerInfo(name='康健药店', type='零售', contact='吴老板', phone='13900139002', address='东区商业街50号'),
            CustomerInfo(name='惠民医药连锁', type='批发', contact='郑总监', phone='13900139003', address='西区工业园'),
            CustomerInfo(name='散客', type='零售', contact='', phone='', address=''),
        ]
        db.session.add_all(customers)
        db.session.commit()
        print(f"✓ 创建了 {len(customers)} 个客户")
        
        # 4. 创建仓库
        warehouses = [
            Warehouse(name='主仓库', address='市区仓储中心A栋', manager_id=2),
            Warehouse(name='分仓库', address='郊区物流园B区', manager_id=2),
        ]
        db.session.add_all(warehouses)
        db.session.commit()
        print(f"✓ 创建了 {len(warehouses)} 个仓库")
        
        # 5. 创建药品
        drug_names = [
            ('阿莫西林胶囊', '0.25g*24粒', '处方'),
            ('感冒灵颗粒', '10g*10袋', '非处方'),
            ('布洛芬缓释胶囊', '0.3g*12粒', '非处方'),
            ('头孢克肟分散片', '50mg*12片', '处方'),
            ('复方甘草片', '100片', '处方'),
            ('维生素C片', '100mg*100片', '非处方'),
            ('阿司匹林肠溶片', '100mg*30片', '处方'),
            ('蒙脱石散', '3g*10袋', '非处方'),
            ('藿香正气水', '10ml*10支', '非处方'),
            ('双黄连口服液', '10ml*12支', '非处方'),
            ('板蓝根颗粒', '10g*20袋', '非处方'),
            ('三九感冒灵', '10g*9袋', '非处方'),
            ('急支糖浆', '120ml', '非处方'),
            ('氨咖黄敏胶囊', '12粒', '非处方'),
            ('罗红霉素胶囊', '150mg*12粒', '处方'),
        ]
        
        drugs = []
        manufacturers = ['扬子江药业', '同仁堂', '三九药业', '999医药', '华润医药']
        
        for i, (name, spec, category) in enumerate(drug_names, 1):
            purchase_price = random.uniform(5, 50)
            sale_price = purchase_price * random.uniform(1.3, 1.8)
            
            drug = DrugInfo(
                name=name,
                spec=spec,
                manufacturer=random.choice(manufacturers),
                approval_number=f'国药准字Z{2020+random.randint(0,3)}{random.randint(100000,999999)}',
                category=category,
                unit='盒',
                purchase_price=round(purchase_price, 2),
                sale_price=round(sale_price, 2),
                expiry_date=(datetime.now() + timedelta(days=random.randint(365, 1095))).date(),
                status='在售'
            )
            drugs.append(drug)
        
        db.session.add_all(drugs)
        db.session.commit()
        print(f"✓ 创建了 {len(drugs)} 个药品")
        
        # 6. 创建入库记录和库存
        print("生成入库记录和库存...")
        for drug in drugs:
            # 每个药品创建1-3次入库记录
            for _ in range(random.randint(1, 3)):
                quantity = random.randint(100, 500)
                stock_in = StockIn(
                    drug_id=drug.drug_id,
                    supplier_id=random.choice(suppliers).supplier_id,
                    quantity=quantity,
                    unit_price=drug.purchase_price,
                    total_price=quantity * drug.purchase_price,
                    stock_in_date=(datetime.now() - timedelta(days=random.randint(1, 90))).date(),
                    employee_id=3,
                    remark='正常采购'
                )
                db.session.add(stock_in)
            
            # 创建库存
            inventory = Inventory(
                drug_id=drug.drug_id,
                warehouse_id=random.choice(warehouses).warehouse_id,
                quantity=random.randint(50, 800),
                location=f'{random.choice(["A", "B", "C"])}-{random.randint(1,20)}-{random.randint(1,5)}',
                last_check_date=(datetime.now() - timedelta(days=random.randint(1, 30))).date()
            )
            db.session.add(inventory)
        
        db.session.commit()
        print("✓ 创建了入库记录和库存")
        
        # 7. 创建销售记录
        print("生成销售记录...")
        for _ in range(100):
            drug = random.choice(drugs)
            quantity = random.randint(1, 20)
            sale = Sales(
                drug_id=drug.drug_id,
                customer_id=random.choice(customers).customer_id,
                quantity=quantity,
                unit_price=drug.sale_price,
                total_price=quantity * drug.sale_price,
                sales_date=(datetime.now() - timedelta(days=random.randint(0, 30))).date(),
                employee_id=1
            )
            db.session.add(sale)
        
        db.session.commit()
        print("✓ 创建了 100 条销售记录")
        
        print("\n🎉 测试数据生成完成！")
        print("\n可以使用以下账号登录：")
        print("  账号: zhangsan, 密码: 123456 (销售经理)")
        print("  账号: lisi, 密码: 123456 (仓管员)")

if __name__ == '__main__':
    init_data()
