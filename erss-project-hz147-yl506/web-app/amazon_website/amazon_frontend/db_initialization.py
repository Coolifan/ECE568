import utils

# --------------------------- DB data initialization --------------------------
conn, cursor = utils.connect_db()

# 1. db cleanup
query = f"""
    TRUNCATE  
    amazon_frontend_orderproducttuple,
    amazon_frontend_warehousestock, 
    amazon_frontend_order, 
    amazon_frontend_product
    CASCADE;

    DELETE FROM amazon_frontend_warehouse;
"""
utils.execute_and_commit(query, conn, cursor)

# 2. create products
query = f"""
    INSERT INTO amazon_frontend_product(name, description, price, seller)
    VALUES
    ('productA', 'A', 1.00, 'Brian'),
    ('productB', 'B', 1.00, 'Brian'),
    ('productC', 'C', 1.00, 'Brian'),
    ('productD', 'D', 1.99, 'Drew');
"""
utils.execute_and_commit(query, conn, cursor)

# 3. create warehouses
query = f"""
    INSERT INTO amazon_frontend_warehouse(location_x, location_y)
    VALUES
    (1, 1),
    (2, 2),
    (3, 3);
"""
utils.execute_and_commit(query, conn, cursor)

query = f"""
    SELECT 
        amazon_frontend_warehouse.id AS warehouse_id, 
        amazon_frontend_product.id AS product_id
    FROM amazon_frontend_warehouse, amazon_frontend_product
"""
cursor.execute(query)
rows = cursor.fetchall()
for warehouse_id, product_id in rows:
    query = f"""
        INSERT INTO amazon_frontend_warehousestock(warehouse_id, product_id, num_product) 
        VALUES({warehouse_id}, {product_id}, 0);
    """
    utils.execute_and_commit(query, conn, cursor)


cursor.close()
# --------------------------- end DB data initialization ---------------------------
