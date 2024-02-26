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


page_title= "Small Business Administration Scorecard"

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
    
# #%%
# def filter_sidebar(data):
#     st.sidebar.header("Choose Your Filter: ")
    
#     #Sort by State Alphabetical Order
#     data = data.dropna(subset='NAICS').sort_values('VENDOR_ADDRESS_STATE_NAME')
    
#     #Create a filter for state
#     state=st.sidebar.multiselect("State",data['VENDOR_ADDRESS_STATE_NAME'].dropna().unique())
    
#     if not state:
#         data2=data.copy()
#         subheader_text=""
#     else:
#         data2=data[data["VENDOR_ADDRESS_STATE_NAME"].isin(state)]
#         subheader_text =f"State: {', '.join(state)}"

#     #Create a filter for SBA Region and District office
#     sba_regions =sorted(data2['SBA_REGION'].dropna().unique(), key =lambda x: int(x.split(' ')[-1]))

#     selected_sba_regions = st.sidebar.multiselect("SBA Region",sba_regions)
#     if not selected_sba_regions:
#         data2=data2.copy()
#         subheader_text_region=""
#     else:
#         data2 = data2[data2["SBA_REGION"].isin(selected_sba_regions)]
#         subheader_text_region =f"{', '.join(selected_sba_regions)}"

#     # Create a filter by SBA District
#     sba_districts = st.sidebar.multiselect("SBA District Office", sorted(data2['SBA_DISTRICT_OFFICE'].dropna().unique()))
#     if not sba_districts:
#         data2=data2.copy()
#         subheader_text_district=""
#     else:
#         data2 = data2[data2["SBA_DISTRICT_OFFICE"].isin(sba_districts)]
#         subheader_text_district =f"SBA District: {', '.join(sba_districts)}" 
    
#     #Create a Filter by Department
#     department=st.sidebar.multiselect("Department", sorted(data2['FUNDING_DEPARTMENT_NAME'].dropna().unique()))
#     if not department:
#         data3=data2.copy()   
#     else:
#         data3=data2[data2["FUNDING_DEPARTMENT_NAME"].isin(department)]
#         department_text=f"Department: {', '.join(department)}"
        
#     #Create a filter by Agency
#     agency=st.sidebar.multiselect("Agency", sorted(data3['FUNDING_AGENCY_NAME'].dropna().unique()))
#     if not agency:
#         data4=data3.copy()
#     else:
#         data4=data3[data3["FUNDING_AGENCY_NAME"].isin(agency)]
   
#     #Create filter for NAICS and PSC code
#     filter_choice=st.sidebar.radio("Select Filter",["NAICS Code","PSC Code"])
#     if filter_choice == 'NAICS Code':
#         codes=st.sidebar.multiselect('NAICS Code', sorted(data4['NAICS'].dropna().unique()))
#         naics_filter =data4['NAICS'].isin(codes)
#         psc_filter=True
#     else:
#         psc_codes =data4['PSC'].dropna().unique()
#         psc_codes = [code for code in psc_codes if code != "N/A: N/A"]
#         codes = st.sidebar.multiselect("PSC Code",sorted(psc_codes))
#         codes_upper = [code.upper() for code in codes]
#         psc_filter=data4['PSC'].str.upper().isin(codes_upper)
#         naics_filter=True

#     #Combine Subheader
#     combined_subheader = f"{subheader_text} {subheader_text_region} {subheader_text_district}"
#     st.subheader(combined_subheader)
 
#     #Create filter for State, Depatrment and Agency
#     #NO selection
#     if not state and not department and not agency and not codes:
#         show_df=data
    
#     #1 Selection
#     #Select State
#     elif not department and not agency and not codes:
#         show_df = data[data["VENDOR_ADDRESS_STATE_NAME"].isin(state)]
#     #Select Department
#     elif not state and not agency and not codes:
#         show_df = data[data["FUNDING_DEPARTMENT_NAME"].isin(department)]
#     #Select Agency
#     elif not state and not department and not codes:
#         show_df = data[data["FUNDING_AGENCY_NAME"].isin(agency)]
   
#     # 3 selections
#     elif department and agency and codes:
#         show_df= data4[data['FUNDING_DEPARTMENT_NAME'].isin(department) & data4['FUNDING_AGENCY_NAME'].isin(agency) & naics_filter & psc_filter]
#     elif state and agency and codes:
#         show_df = data4[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data4['FUNDING_AGENCY_NAME'].isin(agency) & naics_filter & psc_filter]
#     elif state and department and codes:
#         show_df = data4[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data4['FUNDING_DEPARTMENT_NAME'].isin(department) & naics_filter & psc_filter]
#     elif state and department and agency:
#         show_df = data4[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data4['FUNDING_DEPARTMENT_NAME'].isin(department)& data4['FUNDING_AGENCY_NAME'].isin(agency)]

#     # 2 Selections
#     #state
#     elif state and department:
#         show_df = data4[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data4['FUNDING_DEPARTMENT_NAME'].isin(department)]
#     elif state and agency:
#         show_df = data4[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data4['FUNDING_AGENCY_NAME'].isin(agency)]
#     elif state and codes:
#         show_df = data4[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & naics_filter & psc_filter]

#     #department
#     elif department and agency:
#         show_df = data4[data['FUNDING_DEPARTMENT_NAME'].isin(department) & data4['FUNDING_AGENCY_NAME'].isin(agency)]
#     elif department and codes:
#         show_df = data4[data['FUNDING_DEPARTMENT_NAME'].isin(department) & naics_filter & psc_filter]

#     #agency  
#     elif agency and codes:
#         show_df = data4[data['FUNDING_AGENCY_NAME'].isin(agency) & naics_filter & psc_filter]
#     else:
#         show_df =data4[naics_filter & psc_filter]  
#     return show_df

#%%
def filter_sidebar(data):
    st.sidebar.header("Choose Your Filter: ")
    
    #Sort by State Alphabetical Order
    data = data.dropna(subset='NAICS').sort_values('VENDOR_ADDRESS_STATE_NAME')
    
    #Create a filter for state
    state =data['VENDOR_ADDRESS_STATE_NAME'].dropna().unique()
    
    selected_state=st.sidebar.multiselect("State",state)
    
    if not selected_state:
        data2=data.copy()
        subheader_text=""
    else:
        data2=data[data["VENDOR_ADDRESS_STATE_NAME"].isin(selected_state)]
        subheader_text =f"State: {', '.join(selected_state)}"

    #Create a filter for SBA Region and District office
    sba_regions =sorted(data2['SBA_REGION'].dropna().unique(), key =lambda x: int(x.split(' ')[-1]))

    selected_sba_regions = st.sidebar.multiselect("SBA Region",sba_regions)
    if not selected_sba_regions:
        data3=data2.copy()
        subheader_text_region=""
    else:
        data3 = data2[data2["SBA_REGION"].isin(selected_sba_regions)]
        subheader_text_region =f"{', '.join(selected_sba_regions)}"

    # Create a filter by SBA District
    sba_districts = st.sidebar.multiselect("SBA District Office", sorted(data3['SBA_DISTRICT_OFFICE'].dropna().unique()))
    if not sba_districts:
        data4=data3.copy()
        subheader_text_district=""
    else:
        data4 = data3[data3["SBA_DISTRICT_OFFICE"].isin(sba_districts)]
        subheader_text_district =f"SBA District: {', '.join(sba_districts)}" 
    
    #Create a Filter by Department
    department=st.sidebar.multiselect("Department", sorted(data4['FUNDING_DEPARTMENT_NAME'].dropna().unique()))
    if not department:
        data5=data4.copy()   
    else:
        data5=data4[data4["FUNDING_DEPARTMENT_NAME"].isin(department)]
        department_text=f"Department: {', '.join(department)}"
        
    #Create a filter by Agency
    agency=st.sidebar.multiselect("Agency", sorted(data5['FUNDING_AGENCY_NAME'].dropna().unique()))
    if not agency:
        data6=data5.copy()
    else:
        data6=data5[data5["FUNDING_AGENCY_NAME"].isin(agency)]
        
    naics=st.sidebar.multiselect("NAICS Code", sorted(data6['NAICS'].dropna().unique()))
    if not naics:
        data7= data6.copy()
    else:
        data7=data6[data6["NAICS"].isin(naics)]

    #Combine Subheader
    combined_subheader = f"{subheader_text} {subheader_text_region} {subheader_text_district}"
    st.subheader(combined_subheader)
 
    #Create filter for State, Depatrment and Agency
    #NO selection
    if not state and not department and not agency and not naics and not selected_sba_regions and not sba_districts:
        show_df=data

    # One Selection
    # Select State
    elif not selected_sba_regions and not sba_districts and not department and not agency and not naics:
        show_df = data[data["VENDOR_ADDRESS_STATE_NAME"].isin(state)]
    # Select SBA Region
    elif not state and not sba_districts and not department and not agency and not naics:
        show_df = data[data["SBA_REGION"].isin(selected_sba_regions)]
    # Select SBA District Office
    elif not state and not selected_sba_regions and not department and not agency and not naics:
        show_df = data[data["SBA_DISTRICT_OFFICE"].isin(sba_districts)]
    # Select Department
    elif not state and not selected_sba_regions and not sba_districts and not agency and not naics:
        show_df = data[data["FUNDING_DEPARTMENT_NAME"].isin(department)]
    # Select Agency
    elif not state and not selected_sba_regions and not sba_districts and not department and not naics:
        show_df = data[data["FUNDING_AGENCY_NAME"].isin(agency)]
    # Select NAICS
    elif not state and not selected_sba_regions and not sba_districts and not department and not agency:
        show_df = data[data["NAICS"].isin(naics)]

    #Four Selections
    elif state and sba_regions and sba_districts and department:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(selected_state) & data7['SBA_REGION'].isin(selected_sba_regions) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts)& data7['FUNDING_DEPARTMENT_NAME'].isin(department)]
    elif state and sba_regions and sba_districts and agency:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(selected_state) & data7['SBA_REGION'].isin(selected_sba_regions) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7["FUNDING_AGENCY_NAME"].isin(agency)]
    elif state and sba_regions and sba_districts and naics:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(selected_state) & data7['SBA_REGION'].isin(selected_sba_regions) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7["NAICS"].isin(naics)]
    elif state and sba_regions and agency and naics:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(selected_state) & data7['SBA_REGION'].isin(selected_sba_regions) & data7["FUNDING_AGENCY_NAME"].isin(agency)& data7["NAICS"].isin(naics)]
    elif state and sba_districts and department and agency:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(selected_state) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_DEPARTMENT_NAME'].isin(department) & data7["FUNDING_AGENCY_NAME"].isin(agency)]   
    elif state and sba_districts and department and naics:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(selected_state) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_DEPARTMENT_NAME'].isin(department) & data7["NAICS"].isin(naics)]  
    elif state and sba_districts and agency and naics:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(selected_state) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7["FUNDING_AGENCY_NAME"].isin(agency)& data7["NAICS"].isin(naics)] 
    elif state and  department and agency and naics:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(selected_state) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)& data7["FUNDING_AGENCY_NAME"].isin(agency)& data7["NAICS"].isin(naics)]
    
    elif sba_regions and sba_districts and department and agency:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)& data7["FUNDING_AGENCY_NAME"].isin(agency)]
    elif sba_regions and sba_districts and department and agency:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)& data7["NAICS"].isin(naics)]
    elif sba_regions and department and agency and naics:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7['FUNDING_DEPARTMENT_NAME'].isin(department) & data7["FUNDING_AGENCY_NAME"].isin(agency)& data7["NAICS"].isin(naics)]
    elif  sba_districts and department and agency:
        show_df = data7[data['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_DEPARTMENT_NAME'].isin(department) & data7["FUNDING_AGENCY_NAME"].isin(agency)& data7["NAICS"].isin(naics)]
    
    # Three selections
    #State
    elif state and sba_regions and sba_districts:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['SBA_REGION'].isin(selected_sba_regions) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts)]
    elif state and sba_regions and department:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['SBA_REGION'].isin(selected_sba_regions) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)]
    elif state and sba_regions and agency:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['SBA_REGION'].isin(selected_sba_regions) & data7["FUNDING_AGENCY_NAME"].isin(agency)]
    elif state and sba_regions and naics:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['SBA_REGION'].isin(selected_sba_regions) & data7["NAICS"].isin(naics)]
    elif state and sba_districts and department:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)]
    elif state and sba_districts and agency:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7["FUNDING_AGENCY_NAME"].isin(agency)]
    elif state and sba_districts and naics:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7["NAICS"].isin(naics)]
    elif state and  department and agency:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)& data7["FUNDING_AGENCY_NAME"].isin(agency)]
    elif state and  department and naics:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)& data7["NAICS"].isin(naics)]
    elif state and  agency and naics:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7["FUNDING_AGENCY_NAME"].isin(agency) & data7["NAICS"].isin(naics)]
    
    #SBA Region
    elif sba_regions and sba_districts and department:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)]
    elif sba_regions and sba_districts and agency:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7["FUNDING_AGENCY_NAME"].isin(agency)]
    elif sba_regions and sba_districts and naics:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7["NAICS"].isin(naics)]
    elif sba_regions and department and agency:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data['FUNDING_DEPARTMENT_NAME'].isin(department) & data7["FUNDING_AGENCY_NAME"].isin(agency)]
    elif sba_regions and department and naics:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data['FUNDING_DEPARTMENT_NAME'].isin(department) & data7["NAICS"].isin(naics)]
    elif sba_regions and agency and naics:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7["FUNDING_AGENCY_NAME"].isin(agency) & data7["NAICS"].isin(naics)]
    


    #SBA Districts
    elif  sba_districts and department and agency:
        show_df = data7[data['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_DEPARTMENT_NAME'].isin(department) & data7["FUNDING_AGENCY_NAME"].isin(agency)]
    elif  sba_districts and department and naics:
        show_df = data7[data['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_DEPARTMENT_NAME'].isin(department) & data7["NAICS"].isin(naics)]
    elif sba_districts and agency and naics:
        show_df = data7[data['SBA_DISTRICT_OFFICE'].isin(selected_sba_regions) & data7["FUNDING_AGENCY_NAME"].isin(agency) & data7["NAICS"].isin(naics)]


    #Two selections
    #state
    elif state and sba_regions:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['SBA_REGION'].isin(selected_sba_regions)]
    
    elif state and sba_districts:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts)]
    
    elif state and department:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)]
    
    elif state and agency:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['FUNDING_AGENCY_NAME'].isin(agency)]
    elif state and naics:
        show_df = data7[data['VENDOR_ADDRESS_STATE_NAME'].isin(state) & data7['NAICS'].isin(naics)]

    #SBA Region
    elif sba_regions and sba_districts:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7['SBA_DISTRICT_OFFICE'].isin(sba_districts)]
    elif sba_regions and department:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)]
    elif sba_regions and agency:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7['FUNDING_AGENCY_NAME'].isin(agency)]
    elif sba_regions and naics:
        show_df = data7[data['SBA_REGION'].isin(selected_sba_regions) & data7['NAICS'].isin(naics)]
    
    #SBA District
    elif sba_districts and department:
        show_df = data7[data['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_DEPARTMENT_NAME'].isin(department)]
    elif sba_districts and agency:
        show_df = data7[data['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['FUNDING_AGENCY_NAME'].isin(agency)]
    elif sba_districts and naics:
        show_df = data7[data['SBA_DISTRICT_OFFICE'].isin(sba_districts) & data7['NAICS'].isin(naics)]

    #department
    elif department and agency:
        show_df = data7[data['FUNDING_DEPARTMENT_NAME'].isin(department) & data7['FUNDING_AGENCY_NAME'].isin(agency)]
    elif department and naics:
        show_df = data7[data['FUNDING_DEPARTMENT_NAME'].isin(department) & data7['NAICS'].isin(naics)]

    #agency  
    elif agency and naics:
        show_df = data7[data['FUNDING_AGENCY_NAME'].isin(agency) & data7['NAICS'].isin(naics)]
    else:
        show_df =data7['NAICS'].isin(naics)
    return show_df
    
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

    # start_time = time.time()
    # data = get_data()
    # st.write("--- %s seconds get_data ---" % (time.time() - start_time))

    # start_time = time.time()
    # filter = filter_sidebar(data)
    # st.write("--- %s seconds filter_sidebar ---" % (time.time() - start_time))
    
    # start_time = time.time()
    # group_df=group_data_year(filter)
    # st.write("--- %s seconds group_data_year ---" % (time.time() - start_time))
    
    # start_time = time.time()
    # selected_pct= percent_chart(group_df)
    # st.write("--- %s seconds percent_chart ---" % (time.time() - start_time))

    # start_time = time.time()
    # show_table=table_chart_one(group_df) #table dollars 
    # st.write("--- %s seconds table_chart_one ---" % (time.time() - start_time))

    # #percent_table=table_percent(selected_pct) #percent table
    # start_time = time.time()
    # percent_table=table_percent(group_df)
    # st.write("--- %s seconds table_percent ---" % (time.time() - start_time))

    # start_time = time.time()
    # download_df=download_data(group_df,percent_table)#download data
    # st.write("--- %s seconds download_data ---" % (time.time() - start_time))

    # start_time = time.time()
    # expander_df= expander(filter)
    # st.write("--- %s seconds expander---" % (time.time() - start_time))


    st.caption("""Source: SBA Small Business Goaling Reports, FY10-FY22. Location is based on vendor business address. This data does not apply double-credit adjustments and will not match up with the SBA small-business scorecard.\n
Abbreviations: SDB - Small Disadvantaged Business, WOSB - Women-owned small business, HUBZone - Historically Underutilized Business Zone, SDVOSB - Service-disabled veteran-owned small business, 8(a) - 8(a) - Socially and Economically disadvantaged Small Business\n
Total dollars are total scorecard-eligible dollars after applying the exclusions on the [SAM.gov Small Business Goaling Report Appendix](https://sam.gov/reports/awards/standard/F65016DF4F1677AE852B4DACC7465025/view) (login required).""")

   
 