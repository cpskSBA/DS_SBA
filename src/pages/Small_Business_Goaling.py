#%%
import pandas as pd
import streamlit as st
import plotly.express as px
import snowflake.snowpark as sp
import warnings
warnings.filterwarnings('ignore')
from snowflake.snowpark.context import get_active_session
import numpy as np
from snowflake.connector import connect


page_title= "Small Business Goaling"

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
# Columns for numbers and dollar amounts
dolcols=["TOTAL_SB_ACT_ELIGIBLE_DOLLARS","SMALL_BUSINESS_DOLLARS","SDB_DOLLARS","WOSB_DOLLARS","CER_HUBZONE_SB_DOLLARS","SRDVOB_DOLLARS","EIGHT_A_PROCEDURE_DOLLARS"]
# Mapping the renaming of the dollar amount columns
dolcols_rename=["Total$","SmallBusiness$","SDB$","WOSB$","HUBZone$","SDVOSB$","8(a)$"]


#%%
@st.cache_data
def get_data():
    connection_parameters = st.secrets.snowflake_credentials
    global session
    session = sp.Session.builder.configs(connection_parameters).create()
    data = session.table("TMP_SBA_SCORECARD_DASHBOARD_NEW_2")
    data =data.to_pandas()
    return data

#%%
def filter_sidebar(data):
    st.sidebar.header("Choose Your Filter:")
    
    # Create filter options
    filter_options = {
        'State': 'VENDOR_ADDRESS_STATE_NAME',
        'SBA Region': 'SBA_REGION',
        'SBA District': 'SBA_DISTRICT_OFFICE'
    }
    
    # Choose filter
    filter_choice = st.sidebar.radio("Select Filter", list(filter_options.keys()))
    filter_column = filter_options[filter_choice]
    
    # Filter data based on selected filter
    selected_values = st.sidebar.multiselect(filter_choice, sorted(data[filter_column].dropna().unique()))
    filter_condition = data[filter_column].isin(selected_values)
    filtered_data = data[filter_condition] if selected_values else data
    
    # Filter by Department
    department = st.sidebar.multiselect("Department", sorted(filtered_data['FUNDING_DEPARTMENT_NAME'].dropna().unique()))
    filtered_data = filtered_data[filtered_data['FUNDING_DEPARTMENT_NAME'].isin(department)] if department else filtered_data
    
    # Filter by Agency
    agency = st.sidebar.multiselect("Agency", sorted(filtered_data['FUNDING_AGENCY_NAME'].dropna().unique()))
    filtered_data = filtered_data[filtered_data['FUNDING_AGENCY_NAME'].isin(agency)] if agency else filtered_data
    
    # Filter by NAICS
    naics = st.sidebar.multiselect("NAICS Code", sorted(filtered_data['NAICS'].dropna().unique()))
    filtered_data = filtered_data[filtered_data['NAICS'].isin(naics)] if naics else filtered_data
    
    return filtered_data

#%%
@st.cache_data
def group_data_year(show_df):
    year_df = show_df.groupby(['FISCAL_YEAR'],as_index=False)[dolcols].sum()
    doldict={"TOTAL_SB_ACT_ELIGIBLE_DOLLARS":"Total$","SMALL_BUSINESS_DOLLARS":"SmallBusiness$","SDB_DOLLARS":"SDB$","WOSB_DOLLARS":"WOSB$","CER_HUBZONE_SB_DOLLARS":"HUBZone$","SRDVOB_DOLLARS":"SDVOSB$","EIGHT_A_PROCEDURE_DOLLARS":"8(a)$"}
    year_df=year_df.rename(columns=doldict)
    return year_df

def display_chart(data, is_percentage):
    if is_percentage:
        chart_title = "Percentage of Dollars by Category and Year"
    else:
        chart_title = "Cumulative Dollars by Category and Year"
    
    data_long = data.melt(ignore_index=False).rename(columns={"variable": "Category", "value": "Value"})
    data_long.index = data_long.index.astype(str).rename("Fiscal Year")


    pal = ["#002e6d", "#cc0000", "#969696", "#007dbc", "#197e4e", "#f1c400"]
 
    fig = px.line(data_long, x=data_long.index, y="Value", color='Category',
                  color_discrete_sequence=pal,markers=True)
    
    fig.update_layout(xaxis=dict(tickmode='linear'))
    fig.update_layout(xaxis_tickformat='%Y')
    fig.update_traces(mode='markers+lines')
 
    st.subheader(chart_title)
    st.plotly_chart(fig,use_container_width=True)

def percent_chart(year_df):
    is_percentage = st.toggle("View as Percentage", value=True)
    year_df = year_df.set_index('FISCAL_YEAR')
 
    if is_percentage:
        select_pct = year_df.iloc[:, 1:].div(year_df.iloc[:, 0], axis=0).multiply(100).round(2)
        select_pct.columns = select_pct.columns.str.replace("$", "", regex=False)
    else:
        select_pct=year_df[["SmallBusiness$","SDB$","WOSB$","HUBZone$","SDVOSB$","8(a)$"]].copy()
    
    display_chart(select_pct, is_percentage)
    return select_pct

# Create table by Year and dolcols
#%%
def table_chart_one(year_df):
    year_df_chart=year_df.copy()
    year_df_chart[dolcols_rename]=year_df_chart[dolcols_rename].applymap(lambda x: '${:,.0f}'.format(x))
    year_df_chart=year_df_chart.set_index('FISCAL_YEAR')
    st.table(year_df_chart)
    return year_df_chart
   
def table_percent(year_df):
    year_df_pct = year_df.copy().set_index('FISCAL_YEAR')
    year_df_pct = year_df_pct.iloc[:, 1:].div(year_df_pct.iloc[:, 0], axis=0).multiply(100).round(2) 
    year_df_pct.columns = year_df_pct.columns.str.replace("$", "%", regex=False)
    st.table(year_df_pct.style.format('{:.2f}%'))
    return year_df_pct

def download_data(year_df,year_df_pct):
    year_df=year_df.set_index('FISCAL_YEAR')
    merge_df= pd.merge(year_df,year_df_pct, left_index=True, right_index=True)
    merge_df = merge_df[["Total$","SmallBusiness$","SmallBusiness%","SDB$","SDB%","WOSB$","WOSB%","HUBZone$","HUBZone%","SDVOSB$","SDVOSB%","8(a)$","8(a)%"]]
    st.download_button(label="Download Data",data=merge_df.to_csv(),file_name="scorecard.csv")

def expander(show_df):
    if len(show_df) <= 262144:
        with st.expander("CLICK HERE TO VIEW DETAILED DATA (INCLUDING ALL THE COLUMNS LOCATED ON THE LEFT FILTER).", expanded=False):
            detailed_df = show_df.groupby(['FISCAL_YEAR', 'VENDOR_ADDRESS_STATE_NAME', 'FUNDING_DEPARTMENT_NAME', 'FUNDING_AGENCY_NAME','NAICS'], as_index=False)[dolcols].sum()
            doldict = {"TOTAL_SB_ACT_ELIGIBLE_DOLLARS": "Total$", "SMALL_BUSINESS_DOLLARS": "SmallBusiness$", "SDB_DOLLARS": "SDB$",
                       "WOSB_DOLLARS": "WOSB$", "CER_HUBZONE_SB_DOLLARS": "HUBZone$", "SRDVOB_DOLLARS": "SDVOSB$",
                       "EIGHT_A_PROCEDURE_DOLLARS": "8(a)$", 'FISCAL_YEAR': 'Fiscal Year', 'VENDOR_ADDRESS_STATE_NAME': 'Vendor State',
                       'FUNDING_DEPARTMENT_NAME': 'Department', 'FUNDING_AGENCY_NAME': 'Agency', 'NAICS': 'NAICS Code'}
            detailed_df = detailed_df.rename(columns=doldict)
            detailed_df[dolcols_rename] = detailed_df[dolcols_rename].apply(lambda x: round(x,2))  # Round to 2 decimal placeS
            
            percent_df = detailed_df.iloc[:, 6:].div(detailed_df.iloc[:, 5], axis=0).multiply(100)
            percent_df.columns = percent_df.columns.str.replace("$", "%", regex=False)
            merged_df=pd.merge(detailed_df,percent_df,left_index=True, right_index=True)
            merged_df=merged_df[['Fiscal Year', 'Vendor State', 'Department', 'Agency','NAICS Code', 'Total$', 'SmallBusiness$','SmallBusiness%','SDB$','SDB%', 'WOSB$','WOSB%','HUBZone$','HUBZone%','SDVOSB$','SDVOSB%','8(a)$','8(a)%']]
            st.dataframe(merged_df)
            
            #To Download Data
            csv = detailed_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="detailed_data.csv", mime="text/csv",
                               help='Click here to download the data as a CSV file')
    else:
        st.warning("To view a detailed dataset with columns such as Fiscal Year, State, Department, Agency,and NAICS please narrow down the options using the filters on the left.")

if __name__ == "__main__":
    st.header(page_title)
    data = get_data()
    filter = filter_sidebar(data) #Read dataset
    group_df=group_data_year(filter) #Apply Filter
    selected_pct= percent_chart(group_df) #Create groupby dataset
    show_table=table_chart_one(group_df) #Table dollars 
    percent_table=table_percent(group_df) #Percent Table
    download_df=download_data(group_df,percent_table)#Download data
    expander_df= expander(filter)#Create Expander