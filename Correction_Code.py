@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json

    try:
        
        name = data.get('name')
        sku = data.get('sku')
        price = Decimal(str(data.get('price')))
        warehouse_id = data.get('warehouse_id')
        initial_quantity = data.get('initial_quantity', 0)

        if not all([name, sku, price, warehouse_id]):
            return {"error": "Missing required fields"}, 400

        
        if Product.query.filter_by(sku=sku).first():
            return {"error": "SKU must be unique"}, 400

       
        with db.session.begin_nested():
            product = Product(name=name, sku=sku, price=price)
            db.session.add(product)
            db.session.flush()  # Get product.id

            inventory = Inventory(
                product_id=product.id,
                warehouse_id=warehouse_id,
                quantity=initial_quantity
            )
            db.session.add(inventory)

        db.session.commit()
        return {"message": "Product created", "product_id": product.id}

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
