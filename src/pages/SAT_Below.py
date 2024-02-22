#%%
import pandas as pd
import streamlit as st
import plotly.express as px
import snowflake.snowpark as sp
import warnings
warnings.filterwarnings('ignore')
import time
from snowflake.snowpark.context import get_active_session
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode


page_title= "SAT Below Purchases"

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
# Columns to read and group by
basiccols=['VENDOR_ADDRESS_STATE_NAME','FUNDING_DEPARTMENT_NAME','FUNDING_AGENCY_NAME','PRINCIPAL_NAICS_CODE','PRINCIPAL_NAICS_DESCRIPTION','CONTRACTING_DEPARTMENT_NAME','CONTRACTING_AGENCY_NAME','IDV_PIID','MODIFICATION_NUMBER','TYPE_OF_SET_ASIDE']
# Columns for numbers and dollar amounts
dolcols=["ULTIMATE_CONTRACT_VALUE","TOTAL_SB_ACT_ELIGIBLE_DOLLARS","SMALL_BUSINESS_DOLLARS","SDB_DOLLARS","WOSB_DOLLARS","CER_HUBZONE_SB_DOLLARS","SRDVOB_DOLLARS","EIGHT_A_PROCEDURE_DOLLARS"]

# #%%
# @st.cache_data
# def get_data():
#     connection_parameters = st.secrets.snowflake_credentials
#     global session
#     session = sp.Session.builder.configs(connection_parameters).create()
#     data = session.table("SMALL_BUSINESS_GOALING")
#     #data = data.group_by(["FISCAL_YEAR"]+basiccols).sum(*dolcols).to_pandas()
#     data = data[['FISCAL_YEAR','VENDOR_ADDRESS_STATE_NAME','FUNDING_DEPARTMENT_NAME','FUNDING_AGENCY_NAME','PRINCIPAL_NAICS_CODE','PRINCIPAL_NAICS_DESCRIPTION','CONTRACTING_DEPARTMENT_NAME','CONTRACTING_AGENCY_NAME','IDV_PIID','MODIFICATION_NUMBER','TYPE_OF_SET_ASIDE',"ULTIMATE_CONTRACT_VALUE","TOTAL_SB_ACT_ELIGIBLE_DOLLARS","SMALL_BUSINESS_DOLLARS","SDB_DOLLARS","WOSB_DOLLARS","CER_HUBZONE_SB_DOLLARS","SRDVOB_DOLLARS","EIGHT_A_PROCEDURE_DOLLARS"]].to_pandas()


#     data['NAICS']=data['PRINCIPAL_NAICS_CODE'].astype(str) + ': ' + data['PRINCIPAL_NAICS_DESCRIPTION']
#     data.columns = data.columns.str.replace("SUM(","", regex=False).str.replace(")","", regex=False)
#     data=data.dropna(subset=['IDV_PIID','NAICS'])
#     data = data[(data["ULTIMATE_CONTRACT_VALUE"]<= 250000) & (data['MODIFICATION_NUMBER'] == '0')]
#     data['SET_ASIDE']= data.apply(lambda x: 'NOT SET ASIDE' if pd.isna(x['TYPE_OF_SET_ASIDE']) or x['TYPE_OF_SET_ASIDE']=='NONE' else "SET ASIDE", axis =1)
#     data =data.loc[~(data[dolcols]==0).all(axis=1)]
#     data=data[['NAICS','FISCAL_YEAR','SET_ASIDE','VENDOR_ADDRESS_STATE_NAME','FUNDING_DEPARTMENT_NAME','FUNDING_AGENCY_NAME','CONTRACTING_DEPARTMENT_NAME','CONTRACTING_AGENCY_NAME',"ULTIMATE_CONTRACT_VALUE","TOTAL_SB_ACT_ELIGIBLE_DOLLARS","SMALL_BUSINESS_DOLLARS","SDB_DOLLARS","WOSB_DOLLARS","CER_HUBZONE_SB_DOLLARS","SRDVOB_DOLLARS","EIGHT_A_PROCEDURE_DOLLARS"]]
#     return data

#%%
@st.cache_data
def get_data():
    connection_parameters = st.secrets.snowflake_credentials
    global session
    session = sp.Session.builder.configs(connection_parameters).create()
    data = session.table("TMP_BELOW_SAT_DASHBOARD_2")
    data =data.to_pandas()
    # data['SBA_REGION'] = "SBA Region " + data['SBA_REGION']
    # col = basiccols=['VENDOR_ADDRESS_STATE_NAME','FUNDING_DEPARTMENT_NAME','FUNDING_AGENCY_NAME']
    # data[col] = data[col].astype(str)
    # data = data[~data.apply(lambda row: row.astype(str).str.contains('ACTION')).any(axis=1)]
    # data =data.loc[~(data[dolcols]==0).all(axis=1)]
    return data


def filter_sidebar(data):
    filter_choice = st.sidebar.radio("Select Filter", ["Governmentwide", "Funding Department or Agency", "Contracting Department or Agency"])

    data2 = data.copy()  # Define data2 outside the if statement

    if filter_choice == 'Governmentwide':
        pass  # No need to modify data2

    elif filter_choice == "Funding Department or Agency":
        codes_dept = st.sidebar.multiselect('Funding Department Name', sorted(data2['FUNDING_DEPARTMENT_NAME'].dropna().unique()))
        fund_dpt_filter = data2['FUNDING_DEPARTMENT_NAME'].isin(codes_dept)

        codes_agency = st.sidebar.multiselect('Funding Agency Name', sorted(data2['FUNDING_AGENCY_NAME'].dropna().unique()))
        fund_agency_filter = data2['FUNDING_AGENCY_NAME'].isin(codes_agency)

        contr_dpt_filter = True
        contr_agency_filter = True

    else:
        contracting_codes = data2['CONTRACTING_DEPARTMENT_NAME'].dropna().unique()
        codes_dept = st.sidebar.multiselect('Contracting Department Name', sorted(contracting_codes))
        contr_dpt_filter = data2['CONTRACTING_DEPARTMENT_NAME'].isin(codes_dept)

        codes_agency = st.sidebar.multiselect('Contracting Agency Name', sorted(data2['CONTRACTING_AGENCY_NAME'].dropna().unique()))
        contr_agency_filter = data2['CONTRACTING_AGENCY_NAME'].isin(codes_agency)

        fund_dpt_filter = True
        fund_agency_filter = True

    # Create a filter for set_aside
    set_aside = st.sidebar.multiselect('Competition', data2['SET_ASIDE'].dropna().unique())

    if not set_aside:
        data3 = data2.copy()
    else:
        data3 = data2[data2["SET_ASIDE"].isin(set_aside)]

    # Create a filter for fiscal_year
    fiscal_year = st.sidebar.multiselect('Fiscal Year', sorted(data2['FISCAL_YEAR'].dropna().unique()))

    if not fiscal_year:
        data4 = data3.copy()
    else:
        data4 = data3[data3["FISCAL_YEAR"].isin(fiscal_year)]

    # No Choices
    if filter_choice == 'Governmentwide':
        return data2

    elif not codes_dept and not codes_agency and not set_aside and not fiscal_year:
        return data

    # 2 Choices
    elif fiscal_year and set_aside:
        return data4[data["FISCAL_YEAR"].isin(fiscal_year) & data["SET_ASIDE"].isin(set_aside)]

    elif fiscal_year and codes_dept and codes_agency:
        return data4[data['FISCAL_YEAR'].isin(fiscal_year) & fund_dpt_filter & fund_agency_filter & contr_dpt_filter & contr_agency_filter]

    else:
        return data4[data["SET_ASIDE"].isin(set_aside) & fund_dpt_filter & fund_agency_filter & contr_dpt_filter & contr_agency_filter]


    if filter_choice=='Governmentwide':
        return data2
    elif filter_choice == 'Funding Department or Agency':
        return data2[fund_dpt_filter & fund_agency_filter]
    else:
        return data2[contr_dpt_filter &contr_agency_filter]

    return show_df

def group_data_naics(show_df):
    basiccols=['VENDOR_ADDRESS_STATE_NAME','FUNDING_DEPARTMENT_NAME','FUNDING_AGENCY_NAME','CONTRACTING_DEPARTMENT_NAME','CONTRACTING_AGENCY_NAME','IDV_PIID','MODIFICATION_NUMBER','TYPE_OF_SET_ASIDE']
    
    naics_df = show_df.groupby(['NAICS'],as_index=False)['ULTIMATE_CONTRACT_VALUE'].sum()

    return naics_df

if __name__ == "__main__":
    st.header(page_title)
    data = get_data()
    filter = filter_sidebar(data)
    group_df=group_data_naics(filter)
    
