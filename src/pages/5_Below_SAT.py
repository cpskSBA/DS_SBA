#%%
import pandas as pd
import streamlit as st
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')
import numpy as np
from snowflake.connector import connect
import snowflake.snowpark as sp


page_title= "Below SAT Purchases"

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
# Columns for numbers dollar amountsm and percentage
dolcols=["TOTAL_AWARDS","TOTAL_AGGREGATED_DOLLARS","PERCENTAGE_ORDERS_NOT_SET_ASIDE","PERCENTAGE_DOLLARS_NOT_SET_ASIDE","SMALL_BUSINESS_AWARDS_COUNT","SMALL_BUSINESS_AWARDED_DOLLARS","OTHER_THAN_SMALL_BUSINESS_AWARDS_COUNT","OTHER_THAN_SMALL_BUSINESS_AWARDED_DOLLARS"]
# Mapping the renaming of the dollar amount columns
dolcols_rename=["Total # Awards","Total Aggregated $","% Orders NOT SET ASIDE","% $ NOT SET ASIDE","# Small Business Awards","Small Business Awarded $","Other Than Small Business # Awards","Other Than Small Business Awarded $"]
doldict = {k:v for k,v in zip(dolcols, dolcols_rename)}

tb_name = 'BELOW_SAT_DASHBOARD_VIEW'

#%%
@st.cache_resource
def get_data(query, params=None):
    con = connect(**st.secrets.snowflake_credentials)
    cursor = con.cursor()
    if params:
        cursor.execute(query, params)
    else: 
        cursor.execute(query)
    results = cursor.fetch_pandas_all()
    return results

@st.cache_data
def get_columns():
    query = "select COLUMN_NAME from information_schema.columns where table_name = %s"
    cols = get_data(query, (tb_name)).squeeze().to_list()
    return cols

@st.cache_data
def get_filters(cols, linked_cols):
    filters = {}
    for col in cols:
        if col not in dolcols:
            if (col not in linked_cols.keys()) and (col not in linked_cols.values()):
                query = f"select distinct {col} from {tb_name} where {col} !='total'"
                options = get_data(query).squeeze().sort_values().to_list()
                filters[col]=options
            elif col in linked_cols.keys():
                query = f"select distinct {col}, {linked_cols[col]} from {tb_name} where {col} != 'total' and {linked_cols[col]} != 'total'"
                options_tbl = get_data(query)
                options_dict = options_tbl.groupby(col)[linked_cols[col]].apply(list).to_dict()
                filters[col]=options_dict
    #filters = dict(sorted(filters.items()))
    return filters

def sort_filter(filters,column_order):
    return{col:filters[col]for col in column_order if col in filters}

def filter_sidebar(filters, linked_cols):
    st.sidebar.header("Choose Your Filters:")
    selections = {}
    for filter in filters.keys():
        if (filter != 'NAICS') and (filter not in linked_cols.keys()):
            selections[filter] = st.sidebar.multiselect(filter.replace('_',' '), sorted(filters[filter]))
        elif filter in linked_cols.keys():
            selections[filter] = st.sidebar.multiselect(filter.replace('_',' '), sorted(filters[filter].keys()))
            if len(selections[filter]) == 1:
                options=sorted(filters[filter][selections[filter][0]])
            else: options=[]
            selections[linked_cols[filter]] = st.sidebar.multiselect(linked_cols[filter].replace('_',' '), 
                                                                     options,
                                                                     disabled = len(options)==0)
    return selections

def FY_table(cols, selections):
    cols_small = [col for col in cols if col not in dolcols and col != 'NAICS']
    filters = {}
    for col in cols_small:
        if col in selections.keys() and len(selections[col])>0:
            filters[col] = selections[col]
        else: filters[col] = ['total']
    dolcols_str = ', '.join([f'sum({dol}) as {dol}' for dol in dolcols])
    where_str = ' and '.join([f'{k} in (%({k})s)' for k,v in filters.items()]) #Not using this line of code
    query = f"select NAICS, {dolcols_str} from {tb_name} where {where_str} group by NAICS order by 1"  
    FY_table = get_data(query, filters).set_index('NAICS').rename(columns=doldict)
    return FY_table
    
#%%
def table_chart_one(year_df):
    year_df_chart=year_df.copy()
    year_df_chart[dolcols_rename]=year_df_chart[dolcols_rename].applymap(lambda x: '${:,.0f}'.format(x))
    year_df_chart=year_df_chart
    st.dataframe(year_df_chart)
    return year_df_chart

#%%
def table_chart_one(aggregated_df):
    aggregated_df_chart=aggregated_df.copy()
    
    dollars_cols=['Total Aggregated $','Small Business Awarded $','Other Than Small Business Awarded $']
    n_cols= ['Total # Awards','# Small Business Awards','Other Than Small Business # Awards']
    per_cols= ['% Orders NOT SET ASIDE','% $ NOT SET ASIDE']

    aggregated_df_chart[dollars_cols]=aggregated_df_chart[dollars_cols].applymap(lambda x: '${:,.0f}'.format(x))
    aggregated_df_chart[n_cols]=aggregated_df_chart[n_cols].applymap(lambda x: '{:,.0f}'.format(x))
    aggregated_df_chart[per_cols]=aggregated_df_chart[per_cols].applymap(lambda x: '{:,.0f}%'.format(x))
    aggregated_df_chart = aggregated_df_chart.sort_index()
    st.dataframe(aggregated_df_chart)
    return aggregated_df_chart

#%%
@st.cache_data
def get_data_naics():
    connection_parameters = st.secrets.snowflake_credentials
    global session
    session = sp.Session.builder.configs(connection_parameters).create()
    data_naics = session.table("NAICS_VENDOR_COUNT").to_pandas()
    return data_naics

def table_chart_two(data_naics):
    data_naics['SB_PERCENT'] = data_naics['SB_PERCENT'].apply(lambda x: '{:,.2f}%'.format(x))
    data_naics= data_naics.rename(columns={"SMALL_BUSINESS_COUNT":"# of Small Business Vendors","SDB_COUNT":"# of SDB Vendors","WOSB_COUNT":"# of Women-Owned Small Business Vendors","CER_HUBZONE_COUNT":"# of HUBZone Vendors", "SRDVOB_COUNT":"# of Service-Disabled Veteran-Owned Vendors", "EIGHT_A_PROCEDURE_COUNT":"# of 8(a) Vendors",'TOTAL_COUNT':'# of Total Vendors',"SB_PERCENT":"% of Small Business Vendors"}).dropna(subset='NAICS').sort_values("NAICS").set_index('NAICS')
    st.subheader('Count of Vendors by NAICS Code Governmentwide')
    st.dataframe(data_naics)
    return data_naics

if __name__ == "__main__":
    st.header(page_title)
    cols=get_columns()
    linked_cols={'FUNDING_DEPARTMENT_NAME':'FUNDING_AGENCY_NAME', 'CONTRACTING_DEPARTMENT_NAME':'CONTRACTING_AGENCY_NAME'}
    column_order=['FUNDING_DEPARTMENT_NAME','FUNDING_AGENCY_NAME','CONTRACTING_DEPARTMENT_NAME','CONTRACTING_AGENCY_NAME','FISCAL_YEAR','COMPETITION']
    filters = get_filters(cols, linked_cols)
    sorted_filters= sort_filter(filters,column_order)
    
    selections = filter_sidebar(sorted_filters, linked_cols)
    FY_table = FY_table(cols, selections)
    table_chart_one(FY_table)
    data_naics = get_data_naics()
    table_two=table_chart_two(data_naics)

st.caption("""Source: SBA Small Business Goaling Reports, FY10-FY22. This data does not apply double-credit adjustments and will not match up with the SBA small-business scorecard.\n
An award signifies a new award (i.e. Modification Number equals to 0 and where the IDV PIID is not null) for multiple award contracts and neither multiple nor single award contracts. Multiple Award Contracts include (FSS, GWAC, or multiple award IDC).\n
Abbreviations: Total # Awards - Count of total awards given under the NAICS code, Total Aggregated Dollars - Sum of dollars under the NAICS code, % of Orders NOT SET ASIDE - Percent of orders that are NOT A SET ASIDE under the NAICS code, 
           % Dollars NOT SET ASIDE - Percent of dollars that are NOT A SET ASIDE under the NAICS Code, # Small Buiness Awards - Count of awards given to small business under the NAICS Code, Small Business Awarded Dollars - Sum of dollars awared to Small Business under the NAICS code, 
           Other Than Small Business # Awards - Count of awards given to other than small business under the NAICS Code, Other Than Small Business Awarded Dollars - Sum of dollars awared to other than small business under the NAICS Code.""")
