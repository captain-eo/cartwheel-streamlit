import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

st.set_page_config(layout="centered")
# col1, col2 = st.columns([4, 1])

# Retrieve environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def fetch_data(engine, query):
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Fetch all unique usernames from the database
usernames_query = "SELECT DISTINCT username FROM transactions"
usernames_df = fetch_data(engine, usernames_query)
usernames = usernames_df['username'].tolist()

end_date_default = datetime.today().date()
start_date_default = end_date_default - timedelta(days=30)

with st.sidebar:
    # Include date pickers for start date and end date with default values
    start_date = st.date_input("Select start date", value=start_date_default)
    end_date = st.date_input("Select end date", value=end_date_default)

    # Include a dropdown to select a username
    selected_username = st.selectbox("Select username", ["All"] + usernames)

if selected_username == "All":
    query = f"""
    SELECT date_sold, sale_type, sale_total, status, username 
    FROM transactions 
    WHERE date_sold BETWEEN '{start_date}' AND '{end_date}';
    """
else:
    query = f"""
    SELECT date_sold, sale_type, sale_total, status, username 
    FROM transactions 
    WHERE date_sold BETWEEN '{start_date}' AND '{end_date}'
    AND username = '{selected_username}';
    """

# Fetch data from the database
hourly_data = fetch_data(engine, query)

if hourly_data is not None:
    st.header("Transactions by hour")
    # st.write(df.head())
    st.write(f"Total records: {hourly_data.shape[0]}")
    total_sales = hourly_data['sale_total'].sum()
    st.write(f"Total sales: ${total_sales:.2f}")

    # Convert date_sold to datetime
    hourly_data['date_sold'] = pd.to_datetime(hourly_data['date_sold'])

    # Extract hour from date_sold
    hourly_data['hour_sold'] = hourly_data['date_sold'].dt.hour

    # Group data by hour and calculate total sales and number of transactions
    sales_by_hour = hourly_data.groupby('hour_sold')['sale_total'].sum()
    transactions_by_hour = hourly_data.groupby('hour_sold').size()

    # Create bar charts using Streamlit
    st.write("Total Sales by Hour")
    st.bar_chart(sales_by_hour)

    st.write("Number of Transactions by Hour")
    st.bar_chart(transactions_by_hour, color=['#00ff00'])
