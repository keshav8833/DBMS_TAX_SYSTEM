import streamlit as st
from pathlib import Path
import mysql.connector 
import pandas as pd 

import mysql.connector

from datetime import datetime


mydb = mysql.connector.connect(
    host= "localhost",
    user= "Keshav",
    password="keshav772970",
    database = "tax_system"
)


# Mockup of authentication roles
OWNER_USERNAME = "owner"
OWNER_PASSWORD = "owner123"

WORKER_USERNAME = "worker"
WORKER_PASSWORD = "worker123"

# Function to authenticate users
def authenticate(username, password):
    if username == OWNER_USERNAME and password == OWNER_PASSWORD:
        return "owner"
    elif username == WORKER_USERNAME and password == WORKER_PASSWORD:
        return "worker"
    else:
        return None

# Function to check if the user is authenticated
def is_authenticated(user_role):
    return user_role is not None

# Function to render the login page
def render_login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        user_role = authenticate(username, password)
        if is_authenticated(user_role):
            st.session_state.user_role = user_role  # Store user_role in session state
            st.success(f"Login successful! Welcome, {user_role.capitalize()}!")




# Defined functions for orders:



def insert_order(product_name, quant):
    mycursor = mydb.cursor()

    try:
        # SQL query to insert a record
        sql_query = "INSERT INTO orders (P_name, quantity) VALUES (%s, %s)"
        
        # Values to be inserted
        values = (product_name, quant)

        # Execute the query
        mycursor.execute(sql_query, values)

        # Commit the transaction
        mydb.commit()

        print("Record inserted successfully")

    except Exception as e:
        st.error(f"Error: {e}")
        # Rollback in case of an error
        mydb.rollback()

    finally:
        # Close the cursor and mydbection
        mycursor.close()
        mydb.close()


# Defined function for Stock:



def update_stock(product_data):
    mycursor = mydb.cursor()
    
    # Use INSERT ... ON DUPLICATE KEY UPDATE to handle insertion or update
    update_query = """
    INSERT INTO stock (P_id, P_name, quantity, purchase_price, sell_price, gst_percent)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    P_name = VALUES(P_name),
    quantity = quantity + VALUES(quantity),
    purchase_price = VALUES(purchase_price),
    sell_price = VALUES(sell_price),
    gst_percent = VALUES(gst_percent)
    """
    
    mycursor.executemany(update_query, product_data)
    
    mydb.commit()
    st.write("Stock Updated")
    print("Stock updated")

def insert_or_update_customer(name, contact):
    try:
        mycursor = mydb.cursor()

        # Insert customer, update contact and date if it already exists
        insert_query = """
            INSERT INTO customer (name, contact, date)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE contact = VALUES(contact), date =  NOW()
        """

        values = (name, contact)

        mycursor.execute(insert_query, values)
        mydb.commit()

        print("Record inserted or updated")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            st.write(f"Duplicate entry for contact {contact}. Updating the existing record with the current date.")
            # Handle the update logic here
        else:
            print(f"Error: {err}")


# Assume mydb is already defined and connected

# Example usage
  # Update existing customer's contact and date



def get_low_quantity_stock():
    try:
        mycursor = mydb.cursor()
        query = """
        SELECT *
        FROM stock
        WHERE quantity < 100
        """
        mycursor.execute(query)
        low_quantity_stock = mycursor.fetchall()

        columns = [desc[0] for desc in mycursor.description]
    # Create a DataFrame for better display
        df = pd.DataFrame(low_quantity_stock, columns=columns)

        # Display the DataFrame
        st.write(df)        
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")



def insert_tax_information(pan,start_date, end_date, net_profit, total_expense, tax_percentage, tax_amount, total_gst):
    try:
        mycursor = mydb.cursor()

        # Insert tax information into the tax table
        insert_tax_query = """
            INSERT INTO tax (pan,start_date, end_date, net_profit, total_expense, tax_percentage, tax_amount, total_gst)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        tax_values = (pan,start_date, end_date, net_profit, total_expense, tax_percentage, tax_amount, total_gst)

        mycursor.execute(insert_tax_query, tax_values)
        mydb.commit()

        print("Tax information inserted into the tax table")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def search_product(name):
    mycursor = mydb.cursor()
    sql_query = "SELECT * FROM stock WHERE P_name = %s"
    mycursor.execute(sql_query, (name,))
    columns = [desc[0] for desc in mycursor.description]
    records = mycursor.fetchall()
    df = pd.DataFrame(records, columns=columns)
    mycursor.close()
    return df  # Return the DataFrame

def show():
    mycursor = mydb.cursor()
    sql_query = "SELECT * FROM stock"
    mycursor.execute(sql_query)
    records = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    df = pd.DataFrame(records, columns=columns)
    st.write(df)
    mycursor.close()


# Defined function for Expense:

def insert_expense(exp_type, amount):
    mycursor = mydb.cursor()

    try:
        # SQL query to insert a record
        sql_query = "INSERT INTO expense (E_type , amount) VALUES (%s, %s)"
        
        # Values to be inserted
        values = (exp_type, amount)

        # Execute the query
        mycursor.execute(sql_query, values)

        # Commit the transaction
        mydb.commit()
        # Display the inputs
        st.write("Type:", exp_type  , "Amount" , amount) 

        print("Record inserted successfully")

    except Exception as e:
        st.write(f"Error: {e}")
        mydb.rollback()

    finally:
        # Close the cursor and mydbection
        mycursor.close()

# Defined function for Customer:

def display( std , end):
    mycursor = mydb.cursor()
    sql_query = "SELECT * FROM customer WHERE date >= %s AND date <= %s"

    mycursor.execute(sql_query,(std ,end))
    records = mycursor.fetchall()
    # Get column names
    columns = [desc[0] for desc in mycursor.description]

    # Create a DataFrame for better display
    df = pd.DataFrame(records, columns=columns)

    # Display the DataFrame
    st.write(df)




#defined function for tax:
def calculate_total_profit(start_date, end_date):
    mycursor = mydb.cursor()

    # Execute the query to calculate total profit within the date range
    query = """
        SELECT SUM(profit)
        FROM profit
        WHERE Date BETWEEN %s AND %s
    """
    mycursor.execute(query, (start_date, end_date))

    # Fetch the result
    total_profit = mycursor.fetchone()[0]

    # Close the cursor and connection
    mycursor.close()

    return total_profit


def calculate_total_expense(start_date, end_date):
    mycursor = mydb.cursor()
    query = """
        SELECT SUM(amount)
        FROM expense
        WHERE date_of_expenditure BETWEEN %s AND %s
    """
    mycursor.execute(query, (start_date, end_date))

    # Fetch the result
    total_expense = mycursor.fetchone()[0]

    # Close the cursor and connection
    mycursor.close()

    return total_expense

def calculate_gst_amount(start_date, end_date):
    mycursor = mydb.cursor()

    # Execute the query to calculate total GST within the date range
    query = """
        SELECT SUM(gst)
        FROM profit
        WHERE Date BETWEEN %s AND %s
    """
    mycursor.execute(query, (start_date, end_date))

    # Fetch the result
    total_gst = mycursor.fetchone()[0]

    # Close the cursor and connection
    mycursor.close()

    return total_gst






# Function to render the main page
def render_main():
    st.title("K K Traders")
    st.write("Its your shopping make it large!")

    # Create a sidebar
    st.sidebar.title("Menu")

    # Access user_role from session state
    user_role = st.session_state.user_role

    image_url = "KKtraders.png"  # Replace with the actual URL of your image
    st.sidebar.image(image_url, caption="", width= 50)

    # Add content to the sidebar based on the user's role
    if user_role == "owner":
        st.sidebar.write("Welcome, Keshav!")
        selected_page = st.sidebar.radio("Select Page", ["Orders", "Stock", "Expense", "Customer", "Tax"])    
    elif user_role == "worker":
        selected_page = st.sidebar.radio("Select Page", ["Orders", "Stock"])
        st.sidebar.write(f"Welcome, Krishna!")
    else:
        st.sidebar.error("Authentication failed. Please log in.")
    logout_button = st.sidebar.button("Logout")
    if logout_button:
        st.session_state.user_role = None
        st.success("Logout successful!")

    # Add content to the main area based on the selected page
    if user_role in ["owner", "worker"]:

# =================================Orders:========================================

        if selected_page == "Orders":
            st.title("Order Please!")
            st.title("Input Form")

            custom =  st.text_input("Customer Name:", key="customers")
            phone = st.text_input("Phone Number:", key="phones")


            # Provide unique keys for each text_input widget
            prod = st.text_input("Product Name:", key="product_name")
            quantity = st.number_input("Quantity:", min_value=0, value=0, key="quantity")

            # Display the inputs
            st.write("Product Name:", prod)
            st.write("Quantity:", quantity)
            login_button = st.button("ADD")
            if login_button:
                insert_or_update_customer(custom , phone)
                insert_order(prod, quantity)






# ========================================Stock====================================

        elif selected_page == "Stock":
            st.write("Stock page content.")

            produc = st.text_input("Search For Product:", key="product_new")
            login_button = st.button("Enter")

            if login_button:
                result_df = search_product(produc)
                st.title("Search Results")
                st.write(result_df)

            st.title("Present Stock!!")
            refresh = st.button("Refresh Stock")
            if refresh: 
                show()

            st.title("Get Low Quantity Stock")
            get_low_quantity_stock()


            
            st.title("Update Stock:")
            prodid = st.text_input("Product id:", key="product_id")
            prod = st.text_input("Product Name:", key="product")
            quantity = st.number_input("Quantity:", min_value=0, value=0, key="quantity")
            purchase_price = st.number_input("Cost Price:", min_value=0, value=0, key="qty")
            sell_price = st.number_input("Sell Price:", min_value=0, value=0, key="sellprice")
            gst = st.number_input("GST Percent:", min_value=0, value=0, key="gstp")
            product_data = [(prodid, prod, quantity, purchase_price, sell_price, gst)]
            update_button = st.button("update")
            if update_button:
                update_stock(product_data)



# ===================================Expense========================================


        elif selected_page == "Expense":
            st.write("Expense page content.")
            st.title("Input Form")

            # Provide unique keys for each text_input widget
            typeexp = st.text_input("Expense Type:", key="product_name")
            amount = st.number_input("Amount:", min_value=0, value=0, key="quantity")
            login_button = st.button("ADD")
            if login_button:
                insert_expense(typeexp, amount)




# ===============================Customer==================================================


        elif selected_page == "Customer":
            st.write("Customer page content.")
            st.title("My Customers")
            st.write("Enter the Date Interval")
            start_date = st.date_input("from:", key="product_name")
            end_date = st.date_input("to:",  key="quantity")
            login_button = st.button("show")
            if login_button:
                display(start_date , end_date)


# ====================================Tax====================================================


        elif selected_page == "Tax":
            mycursor = mydb.cursor()
            st.title("Calculate Total Profit")
            start_date = st.date_input("Select Start Date")
            end_date = st.date_input("Select End Date")
            check = st.button("Check")
            sql_query = "SELECT pan FROM tax_payer"
            mycursor.execute(sql_query)

        # Fetch the result
            pan_number = mycursor.fetchone()
            print(pan_number)
            
            if check:
                if start_date and end_date:
                    result = calculate_total_profit(start_date, end_date)
                    st.write(f'Total Profit from <b>{start_date}</b> to <b>{end_date}</b>: <b>{result}</b>', unsafe_allow_html=True)
                if start_date and end_date:
                    result_expense = calculate_total_expense(start_date, end_date)
                    st.write(f'Total Expense from <b>{start_date}</b> to <b>{end_date}</b>: <b>{result_expense}</b>', unsafe_allow_html=True)
                if start_date and end_date:
                    result_gst = calculate_gst_amount(start_date, end_date)
                    
                net_profit  = result - result_expense
                st.write("Net Profit Made:", net_profit)

                tax_percentage = 0
                if net_profit > 20000:
                    tax_percentage = 0.3
                elif net_profit > 10000:
                    tax_percentage = 0.1
                elif net_profit > 5000:
                    tax_percentage = 0.05

                tax_amount = net_profit * tax_percentage
                st.write(f'Tax ({tax_percentage * 100}%): <b>{tax_amount}</b>', unsafe_allow_html=True)
                st.write(f'Total GST Amount from <b>{start_date}</b> to <b>{end_date}</b>: <b>{result_gst}</b>', unsafe_allow_html=True)
                insert_tax_information(pan_number[0],start_date, end_date,  result, result_expense, tax_percentage, tax_amount, tax_amount)


# Function to render the logout button
def render_logout():
    logout_button = st.button("Logout")
    if logout_button:
        st.session_state.user_role = None
        st.success("Logout successful!")

# Main function
def main():
    # Initialize session state if not present
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

    # Check if the user is authenticated
    if not is_authenticated(st.session_state.user_role):
        render_login()
    else:
        render_main()

if __name__ == "__main__":
    main()
