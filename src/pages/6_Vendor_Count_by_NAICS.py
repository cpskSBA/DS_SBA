#%%
import pandas as pd
import streamlit as st
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')
import numpy as np
from snowflake.connector import connect
import snowflake.snowpark as sp

page_title= "Vendor Count by NAICS Code"

st.set_page_config(
    page_title=page_title,
    page_icon="https://www.sba.gov/brand/assets/sba/img/pages/logo/logo.svg",
    layout="wide",
    initial_sidebar_state="expanded")

hide_streamlit_style = """
             <style>
             footer {visibility: hidden;}
             </style>
             """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

#%%
@st.cache_data
def get_data_naics():
    connection_parameters = st.secrets.snowflake_credentials
    global session
    session = sp.Session.builder.configs(connection_parameters).create()
    data_naics = session.table("NAICS_VENDOR_COUNT").to_pandas()
    return data_naics

def table_chart_two(data_naics):
    #data_naics['SB_PERCENT'] = data_naics['SB_PERCENT'].apply(lambda x: '{:,.2f}%'.format(x))
    data_naics= data_naics.rename(columns={"SMALL_BUSINESS_COUNT":"# of Small Business Vendors","SDB_COUNT":"# of SDB Vendors","WOSB_COUNT":"# of Women-Owned Small Business Vendors","CER_HUBZONE_COUNT":"# of HUBZone Vendors", "SRDVOB_COUNT":"# of Service-Disabled Veteran-Owned Vendors", "EIGHT_A_PROCEDURE_COUNT":"# of 8(a) Vendors",'TOTAL_COUNT':'# of Total Vendors',"SB_PERCENT":"% of Small Business Vendors"}).dropna(subset='NAICS').sort_values("NAICS").set_index('NAICS')
    st.subheader('Count of Vendors by NAICS Code Governmentwide')
    st.dataframe(data_naics)
    return data_naics

if __name__ == "__main__":
    st.header(page_title)
    data_naics = get_data_naics()
    table_two=table_chart_two(data_naics)