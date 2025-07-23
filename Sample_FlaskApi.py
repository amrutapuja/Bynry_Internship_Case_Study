@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):
    # Assumes `db.session` and SQLAlchemy models are used
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Subquery: recent sales
    recent_sales_subq = db.session.query(Sale.product_id).filter(
        Sale.created_at >= thirty_days_ago
    ).distinct().subquery()

    # Join inventory + products + warehouses + suppliers
    results = db.session.query(
        Inventory.product_id,
        Product.name,
        Product.sku,
        Inventory.warehouse_id,
        Warehouse.name.label('warehouse_name'),
        Inventory.quantity,
        Product.threshold,
        Supplier.id.label('supplier_id'),
        Supplier.name.label('supplier_name'),
        Supplier.contact_email
    ).join(Product, Product.id == Inventory.product_id
    ).join(Warehouse, Warehouse.id == Inventory.warehouse_id
    ).outerjoin(SupplierProduct, SupplierProduct.product_id == Product.id
    ).outerjoin(Supplier, Supplier.id == SupplierProduct.supplier_id
    ).filter(
        Warehouse.company_id == company_id,
        Product.id.in_(recent_sales_subq),
        Inventory.quantity < Product.threshold
    ).all()

    alerts = []
    for r in results:
        days_until_stockout = random.randint(5, 15)  # Placeholder logic
        alerts.append({
            "product_id": r.product_id,
            "product_name": r.name,
            "sku": r.sku,
            "warehouse_id": r.warehouse_id,
            "warehouse_name": r.warehouse_name,
            "current_stock": r.quantity,
            "threshold": r.threshold,
            "days_until_stockout": days_until_stockout,
            "supplier": {
                "id": r.supplier_id,
                "name": r.supplier_name,
                "contact_email": r.contact_email
            } if r.supplier_id else None
        })

    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts)
    })
