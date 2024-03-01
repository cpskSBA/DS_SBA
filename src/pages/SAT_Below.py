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
# Columns to read and group by
#basiccols=['VENDOR_ADDRESS_STATE_NAME','FUNDING_DEPARTMENT_NAME','FUNDING_AGENCY_NAME','PRINCIPAL_NAICS_CODE','PRINCIPAL_NAICS_DESCRIPTION','CONTRACTING_DEPARTMENT_NAME','CONTRACTING_AGENCY_NAME','IDV_PIID','MODIFICATION_NUMBER','TYPE_OF_SET_ASIDE']
# Columns for numbers and dollar amounts
#dolcols=["ULTIMATE_CONTRACT_VALUE","TOTAL_SB_ACT_ELIGIBLE_DOLLARS","SMALL_BUSINESS_DOLLARS","SDB_DOLLARS","WOSB_DOLLARS","CER_HUBZONE_SB_DOLLARS","SRDVOB_DOLLARS","EIGHT_A_PROCEDURE_DOLLARS"]

#%%
@st.cache_data
def get_data():
    connection_parameters = st.secrets.snowflake_credentials
    global session
    session = sp.Session.builder.configs(connection_parameters).create()
    data = session.table("TMP_BELOW_SAT_DASHBOARD_2")
    data =data.to_pandas()
    return data

#%%
def filter_sidebar(data):
    st.sidebar.header("Choose Your Filter: ")
    
    #Sort by State Alphabetical Order
    #data = data.dropna(subset=["FUNDING_AGENCY_NAME",]).sort_values('VENDOR_ADDRESS_STATE_NAME')

    #Create filter for State and SBA Region and SBA DIstrict
    filter_choice=st.sidebar.radio("Select Filter",["Funding Department","Funding Agency", "Contracting Department", "Contracting Agency"])
    
    if filter_choice == 'Funding Department':
        codes=st.sidebar.multiselect('Funding Department', sorted(data['FUNDING_DEPARTMENT_NAME'].dropna().unique()))
        f_dept_filter =data['FUNDING_DEPARTMENT_NAME'].isin(codes)
        f_dept_filter_naics=data[f_dept_filter]['NAICS'].unique()

        f_agency_filter =True
        c_dept_filter =True
        c_agency_filter = True
       
        data2=data.copy() if not f_dept_filter.any() else data[data["FUNDING_DEPARTMENT_NAME"].isin(codes)]
        
    elif filter_choice == 'Funding Agency':
        codes=st.sidebar.multiselect('Funding Agency', sorted(data['FUNDING_AGENCY_NAME'].dropna().unique()))
        f_agency_filter =data['FUNDING_AGENCY_NAME'].isin(codes)
        
        f_dept_filter =True
        c_dept_filter =True
        c_agency_filter = True
        
        data2=data.copy() if not f_agency_filter.any() else data[data["FUNDING_AGENCY_NAME"].isin(codes)]
        
    elif filter_choice == 'Contracting Department':
        codes=st.sidebar.multiselect('Contracting Department',sorted(data['CONTRACTING_DEPARTMENT_NAME'].dropna().unique()))
        c_dept_filter =data['CONTRACTING_DEPARTMENT_NAME'].isin(codes)
        
        f_agency_filter =True
        f_dept_filter =True
        c_agency_filter = True
        
        data2=data.copy() if not c_dept_filter.any() else data[data["CONTRACTING_DEPARTMENT_NAME"].isin(codes)]
        
    else:
         codes = st.sidebar.multiselect("Contracting Agency",sorted(data['CONTRACTING_AGENCY_NAME'].dropna().unique()))
         c_agency_filter =data['CONTRACTING_AGENCY_NAME'].isin(codes)
         
         f_agency_filter =True
         f_dept_filter =True
         c_dept_filter = True
         
         data2=data.copy() if not c_agency_filter.any() else data[data["CONTRACTING_AGENCY_NAME"].isin(codes)]
        
    
    #Create a Filter by Competition
    competition=st.sidebar.multiselect("Competition", sorted(data2['SET_ASIDE'].dropna().unique()))
    
    if not competition:
        data3=data2.copy()   
    else:
        data3=data2[data2["SET_ASIDE"].isin(competition)]
        
        
    #Create a filter by fISCAL YEAR
    year=st.sidebar.multiselect("Fiscal Year", sorted(data3['FISCAL_YEAR'].dropna().unique()))
    # if not year:
    #     data4=data3.copy()   
    # else:
    #     data4=data3[data3['FISCAL_YEAR'].isin(year)]

    #  #Create a filter by award type
    # award=st.sidebar.multiselect("Award Type", sorted(data4['AWARD_TYPE'].dropna().unique()))
    

    #Create filter for State, Depatrment and Agency
    #NO selection
    if not codes and not competition and not year:
        show_df=data

    #1 Selection
    #Select State
    elif not competition and not year:
        show_df = data[f_dept_filter & f_agency_filter & c_dept_filter & c_agency_filter]
    #Select Department
    elif not codes and not competition:
        show_df = data[data["FISCAL_YEAR"].isin(year)]
    #Select Agency
    elif not codes and not year:
        show_df = data[data["SET_ASIDE"].isin(competition)]
    #Select award type
    elif not codes and not competition and not year:
        show_df = data[data["AWARD_TYPE"].isin(year)]

    #All selection
    elif codes and competition and year:
        show_df = data3[f_dept_filter & f_agency_filter & c_dept_filter & c_agency_filter & data3['SET_ASIDE'].isin(competition)& data3['FISCAL_YEAR'].isin(year)]

    
    # # 3 selections
    # elif codes and competition and year:
    #     show_df = data4[f_dept_filter & f_agency_filter & c_dept_filter & c_agency_filter & data4['SET_ASIDE'].isin(competition)& data4['FISCAL_YEAR'].isin(year)]

    # elif codes and competition and award:
    #     show_df = data4[f_dept_filter & f_agency_filter & c_dept_filter & c_agency_filter & data4['SET_ASIDE'].isin(competition)& data4['AWARD_TYPE'].isin(award)]

    # elif competition and year and award:
    #     show_df = data4[data['SET_ASIDE'].isin(competition)& data4['FISCAL_YEAR'].isin(year)& data4['AWARD_TYPE'].isin(award)]

    #2 selections
        #Codes
    elif codes and competition:
        show_df = data3[f_dept_filter & f_agency_filter & c_dept_filter & c_agency_filter & data3['SET_ASIDE'].isin(competition)]

    elif codes and year:
        show_df = data3[f_dept_filter & f_agency_filter & c_dept_filter & c_agency_filter & data3['FISCAL_YEAR'].isin(year)]

    # elif codes and award:
    #     show_df = data4[f_dept_filter & f_agency_filter & c_dept_filter & c_agency_filter & data4['AWARD_TYPE'].isin(award)]

        #Competition
    # elif competition and year:
    #     show_df = data4[data['SET_ASIDE'].isin(competition)& data4['FISCAL_YEAR'].isin(year)]
    # elif competition and award:
    #     show_df = data4[data['SET_ASIDE'].isin(competition)& data4['AWARD_TYPE'].isin(award)]

        #Fiscal Year
    # elif year and award:
    #     show_df = data4[data['FISCAL_YEAR'].isin(year)& data4['AWARD_TYPE'].isin(award)]

    # else:
    #     show_df =data4[data['AWARD_TYPE'].isin(award)] 

    
    return show_df 
    
#%%
def group_data_naics(show_df):

    grouped = show_df.groupby('NAICS')

# Define a function to calculate the aggregated values for each NAICS group 
    def calculate_aggregates(group):
    # Total Awards under SAT
        total_awards_sat = len(group)

        # Total Aggregate Dollars under SAT
        total_dollars_sat = group['TOTAL_SB_ACT_ELIGIBLE_DOLLARS'].sum()

        # Percentage of orders that are not set aside under the SAT
        total_not_set_aside = group[group['SET_ASIDE'] == 'NOT A SET ASIDE']
        percentage_orders_not_set_aside = (len(total_not_set_aside) / total_awards_sat) * 100 if total_awards_sat > 0 else 0
         
        # Percentage of dollars on orders that are not set aside under the SAT
        dollars_not_set_aside = total_not_set_aside['TOTAL_SB_ACT_ELIGIBLE_DOLLARS'].sum()
        percentage_dollars_not_set_aside = (dollars_not_set_aside / total_dollars_sat) * 100 if total_dollars_sat > 0 else 0

        # Awards under SAT to Small Business
        small_business_awards = group[group['CO_BUS_SIZE_DETERMINATION'] == 'SMALL BUSINESS']
        small_business_awards_count = len(small_business_awards)
        small_business_dollars = small_business_awards['TOTAL_SB_ACT_ELIGIBLE_DOLLARS'].sum()

        # Awards under SAT to Other Than Small Business
        other_than_small_business_awards = group[group['CO_BUS_SIZE_DETERMINATION'] == 'OTHER THAN SMALL BUSINESS']
        other_than_small_business_awards_count = len(other_than_small_business_awards)
        other_than_small_business_dollars = other_than_small_business_awards['TOTAL_SB_ACT_ELIGIBLE_DOLLARS'].sum()

        return pd.Series({
            'Total # Awards': total_awards_sat,
            'Total Aggregated $': total_dollars_sat,
            '% Orders NOT SET ASIDE': percentage_orders_not_set_aside,
            '% $ NOT SET ASIDE': percentage_dollars_not_set_aside,
            
            '# SB Awards': small_business_awards_count,
            'SB Awarded $': small_business_dollars,
            
            'Other Than SB # Awards': other_than_small_business_awards_count,
            'Other Than SB Awarded $': other_than_small_business_dollars
        })

    # Apply the function to each group and concatenate the results 
    aggregated_df = grouped.apply(calculate_aggregates).reset_index()

# Return the aggregated DataFrame
    return aggregated_df

def table_chart_one(aggregated_df):
    aggregated_df_chart=aggregated_df.copy()
    
    dollars_cols=['Total Aggregated $','SB Awarded $','Other Than SB Awarded $']
    n_cols= ['Total # Awards','# SB Awards','Other Than SB # Awards']
    per_cols= ['% Orders NOT SET ASIDE','% $ NOT SET ASIDE']

    aggregated_df_chart[dollars_cols]=aggregated_df_chart[dollars_cols].applymap(lambda x: '${:,.0f}'.format(x))
    aggregated_df_chart[n_cols]=aggregated_df_chart[n_cols].applymap(lambda x: '{:,.0f}'.format(x))
    aggregated_df_chart[per_cols]=aggregated_df_chart[per_cols].applymap(lambda x: '{:,.0f}%'.format(x))
    
    aggregated_df_chart=aggregated_df_chart.sort_values('NAICS').set_index('NAICS')
    st.dataframe(aggregated_df_chart)
    return aggregated_df_chart

if __name__ == "__main__":
    st.header(page_title)
    data = get_data()
    filter = filter_sidebar(data)
    group_df=group_data_naics(filter)
    table=table_chart_one(group_df)

st.caption("""Source: SBA Small Business Goaling Reports, FY10-FY22. This data does not apply double-credit adjustments and will not match up with the SBA small-business scorecard.\n
An award signifies a new award (i.e. Modification Number equals to 0 and where the IDV PIID is not null) for multiple award contracts and neither multiple nor single award contracts. Multiple Award Contracts include (FSS, GWAC, or multiple award IDC).
Abbreviations:Total # Awards - Count of Total Awards given under the NAICS code, Total Aggregated $ - Sum of Dollars under the NAICS code, % Orders NOT SET ASIDE - Percent of Orders that are NOT A SET ASIDE under the NAICS Code',
% $ NOT SET ASIDE - Percent of Dollars that are NOT A SET ASIDE under the NAICS Code, # SB Awards - Count of Awards given to Small Business under the NAICS Code, SB Awarded $ - Sum of Dollars awared to Small Business under the NAICS Code'
Other Than SB # Awards - Count of Awards given to Other Than Small Business under the NAICS Code, Other Than SB Awarded $ - Sum of Dollars awared to Other than Small Business under the NAICS Code.\n
Total dollars are total scorecard-eligible dollars after applying the exclusions on the [SAM.gov Small Business Goaling Report Appendix](https://sam.gov/reports/awards/standard/F65016DF4F1677AE852B4DACC7465025/view) (login required).""")

