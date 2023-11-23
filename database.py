import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="Keshav",
    password="keshav772970",
    database="tax_system"
)



def create_table_tax_payer_if_not_exists():
    mycursor = mydb.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS tax_payer (
        pan varchar(10) NOT NULL PRIMARY KEY,
        name varchar(255) NOT NULL,
        dob date NOT NULL,
        address varchar(255) NOT NULL,
        contact varchar(10) NOT NULL    
    )    
    """    
    mycursor.execute(create_table_query)

    print("Table created")



def create_table_expense_if_not_exists():
    mycursor = mydb.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS expense (
        E_id int AUTO_INCREMENT PRIMARY KEY,
        E_type varchar(255) NOT NULL,
        amount float NOT NULL,
        date_of_expenditure date NOT NULL
    )
    """
    mycursor.execute(create_table_query)

    print("Table created")


def create_table_stock_if_not_exists():
    mycursor = mydb.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS stock (
        P_id varchar(10) NOT NULL PRIMARY KEY,
        P_name varchar(255) NOT NULL,
        quantity int DEFAULT NULL CHECK (quantity >= 0),
        purchase_price float NOT NULL,
        sell_price float NOT NULL,
        gst_percent int NOT NULL
    )
    """
    mycursor.execute(create_table_query)

    print("Table created")




def create_table_customer_if_not_exists():
    mycursor = mydb.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS customer (
        name varchar(255) NOT NULL,
        contact varchar(10) NOT NULL PRIMARY KEY,
        date Date NOT NULL,
        frequency int NOT NULL
    )
    """
    mycursor.execute(create_table_query)

    print("Table created")

def create_table_tax_if_not_exists():
    mycursor = mydb.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS tax (
        pan varchar(10) NOT NULL,
        tax_id INT AUTO_INCREMENT PRIMARY KEY,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        net_profit FLOAT NOT NULL,
        total_expense FLOAT NOT NULL,
        tax_percentage FLOAT NOT NULL,
        tax_amount FLOAT NOT NULL,
        total_gst FLOAT NOT NULL
    )
    """
    mycursor.execute(create_table_query)
    print("Table created Tax")

# Call the function to create the tax table if it doesn't exist
create_table_tax_if_not_exists()

    
def create_table_orders_if_not_exists():
    mycursor = mydb.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS orders (
        O_id INT AUTO_INCREMENT PRIMARY KEY,
        P_name VARCHAR(225),
        quantity INT,
        date DATE
    )
    """



    # datequery = "UPDATE orders SET date = curDate();"

    mycursor.execute(create_table_query)
    # mycursor.execute(datequery)

    print("Table created")




def create_trigger_reduce_quantity():
    mycursor = mydb.cursor()

    # Create trigger to reduce quantity from stock after an order is inserted
    trigger_query = """
    CREATE TRIGGER if not exists reduce_quantity_trigger
    AFTER INSERT ON orders
    FOR EACH ROW
    UPDATE stock
    SET quantity = quantity - NEW.quantity
    WHERE P_id = GetProductId (New.P_name);
    """
    mycursor.execute(trigger_query)

    print("Trigger created")
def date_trig():
    mycursor = mydb.cursor()
    date_query = """
        CREATE TRIGGER if not exists set_default_date
        BEFORE INSERT ON orders
        FOR EACH ROW
        SET NEW.date = IFNULL(NEW.date, CURDATE());
    """
    mycursor.execute(date_query)

    print("Trigger for date created")


def date_trig_Customer():
    mycursor = mydb.cursor()
    date_query = """
        CREATE TRIGGER if not exists set_default_date_customer
        BEFORE INSERT ON customer
        FOR EACH ROW
        SET NEW.date = IFNULL(NEW.date, CURDATE());
    """
    mycursor.execute(date_query)

    print("Trigger for date created")

def date_trig_for_expense():
    mycursor = mydb.cursor()
    date_query = """
        CREATE TRIGGER if not exists set_default_date_expense
        BEFORE INSERT ON expense
        FOR EACH ROW
        SET NEW.date_of_expenditure = IFNULL(NEW.date_of_expenditure, CURDATE());
    """
    mycursor.execute(date_query)

    print("Trigger for expense created")



def create_table_profit():
    mycursor = mydb.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS profit (
        O_id INT AUTO_INCREMENT PRIMARY KEY,
        Date DATE,
        P_name VARCHAR(255),
        quantity INT,
        purchase_price float,
        sell_price float,
        gst_percent int,
        profit float,
        gst float   
    )
    """
    mycursor.execute(create_table_query)

    print("Table 'profit' created")

def generate_profit_table():
    mycursor = mydb.cursor()

    # Join orders and stock tables and calculate profit
    join_query = """
    INSERT INTO profit (Date, P_name, quantity, purchase_price, sell_price, gst_percent, profit, gst)
    SELECT
        orders.date,
        orders.P_name,
        orders.quantity,
        stock.purchase_price,
        stock.sell_price,
        stock.gst_percent,
        (orders.quantity * (stock.sell_price - stock.purchase_price)) AS profit,
        (orders.quantity* stock.purchase_price * stock.gst_percent/100) as gst
    FROM
        orders
    JOIN
        stock ON orders.P_name = stock.P_name
    """
    mycursor.execute(join_query)

    mydb.commit()
    print("Profit table generated")


def create_trigger_update_profit():
    mycursor = mydb.cursor()
    create_trigger_query = """
    CREATE TRIGGER if not exists update_profit
    AFTER INSERT ON orders
    FOR EACH ROW
    BEGIN
        INSERT INTO profit (Date, P_name, quantity, purchase_price, sell_price, gst_percent, profit, gst)
        SELECT
            NEW.date,
            NEW.P_name,
            NEW.quantity,
            stock.purchase_price,
            stock.sell_price,
            stock.gst_percent,
            (NEW.quantity * (stock.sell_price - stock.purchase_price)) AS profit,
            (NEW.quantity * stock.purchase_price * stock.gst_percent /100) as gst
        FROM
            stock
        WHERE
            stock.P_name = NEW.P_name;
    END;
    """
    mycursor.execute(create_trigger_query)

    print("Trigger 'update_profit' created")


# def insert_or_update_customer(name, contact):
#     mycursor = mydb.cursor()

#     insert_query = """
#         INSERT INTO customer (name, contact)
#         VALUES (%s, %s)
#         ON DUPLICATE KEY 
#     """

#     values = (name, contact)
    
#     mycursor.execute(insert_query, values)
#     mydb.commit()

#     print("Record inserted or updated")




def main():
    mycursor = mydb.cursor()
    create_table_tax_payer_if_not_exists()
    create_table_stock_if_not_exists()
    create_table_expense_if_not_exists()
    create_table_customer_if_not_exists()
    create_table_orders_if_not_exists()
    create_trigger_reduce_quantity()
    date_trig()
    date_trig_Customer()
    create_table_profit()
    create_trigger_update_profit()
    date_trig_for_expense()
    # generate_profit_table()
    # insert_or_update_customer("Keshav" , "8521772975")


if __name__ == "__main__":
    main()

