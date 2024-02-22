#%%
import polars as pl
import pandas as pd
import streamlit as st
import plotly.express as px
import pyarrow.dataset as ds
import os
import pyarrow as pa
import json
import plotly.graph_objects as go

# datalake="C:\\Users\\SQLe\\U.S. Small Business Administration\\Office of Policy Planning and Liaison (OPPL) - Data Lake\\"

# arrowds=ds.dataset(f"{datalake}/SBGR_parquet",format="parquet",partitioning = ds.HivePartitioning(
#     pa.schema([("FY", pa.int16())])))
# plds=pl.scan_ds(arrowds)

# max_year = int(os.listdir(f"{datalake}/SBGR_parquet")[-1].replace("FY=",""))
# min_year = int(os.listdir(f"{datalake}/SBGR_parquet")[0].replace("FY=",""))
max_year=2022
min_year=2009
# %%
st.set_page_config(
    page_title="SBA Vendor Count",
    page_icon="https://www.sba.gov/brand/assets/sba/img/pages/logo/logo.svg",
   # layout="wide",
    initial_sidebar_state="expanded",
)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
#%%
#extract vendor data
vendorcols=["VENDOR_DUNS_NUMBER","VENDOR_UEI"]
geocols=["VENDOR_ADDRESS_STATE_NAME","CONGRESSIONAL_DISTRICT"
         ,'VENDOR_ADDRESS_ZIP_CODE',]
buyercols=['FUNDING_DEPARTMENT_NAME','FUNDING_AGENCY_NAME']
contractcols=['IDV_TYPE_OF_SET_ASIDE','TYPE_OF_SET_ASIDE','PRINCIPAL_NAICS_CODE']
dolcols=["TOTAL_SB_ACT_ELIGIBLE_DOLLARS","SMALL_BUSINESS_DOLLARS","SDB_DOLLARS","WOSB_DOLLARS","CER_HUBZONE_SB_DOLLARS","SRDVOB_DOLLARS"]

vendor_dict={"TOTAL_SB_ACT_ELIGIBLE_DOLLARS":"All Vendors"
            ,"SMALL_BUSINESS_DOLLARS":"Small Business Vendors"
            ,"SDB_DOLLARS":"SDB Vendors"
            ,"WOSB_DOLLARS":"WOSB Vendors"
            ,"CER_HUBZONE_SB_DOLLARS":"HUBZone Vendors"
            ,"SRDVOB_DOLLARS":"SDVOSB Vendors"
    }
newdolcols=list(vendor_dict.values())

set_aside_dict={
        "SBA":"Small Business Set-Aside",
        "RSB":"Small Business Set-Aside",
        "ESB":"Small Business Set-Aside",
        "SBP":"Partial SB Set-Aside",
        "8A":"8(a) Competitive",
        "8AN":"8(a) Sole Source",
        "WOSB":"WOSB Set-Aside",
        "WOSBSS":"WOSB Sole Source",
        "EDWOSB":"EDWOSB Set-Aside",
        "EDWOSBSS":"EDWOSB Sole Source",
        "SDVOSBC":"SDVOSB Set-Aside",
        "SDVOSBS":"SDVOSB Sole Source",
        "HS3":"HUBZone Set-Aside",
        "HZC":"HUBZone Set-Aside",
        "HZS":"HUBZone Sole Source",
    }
department_select=['AGENCY FOR INTERNATIONAL DEVELOPMENT', 'AGRICULTURE, DEPARTMENT OF', 'COMMERCE, DEPARTMENT OF'
          ,'DEPT OF DEFENSE', 'EDUCATION, DEPARTMENT OF', 'ENERGY, DEPARTMENT OF'
          ,'ENVIRONMENTAL PROTECTION AGENCY', 'GENERAL SERVICES ADMINISTRATION', 'HEALTH AND HUMAN SERVICES, DEPARTMENT OF'
          ,'HOMELAND SECURITY, DEPARTMENT OF', 'HOUSING AND URBAN DEVELOPMENT, DEPARTMENT OF', 'INTERIOR, DEPARTMENT OF THE'
          ,'JUSTICE, DEPARTMENT OF', 'LABOR, DEPARTMENT OF', 'NATIONAL AERONAUTICS AND SPACE ADMINISTRATION'
          ,'NATIONAL SCIENCE FOUNDATION', 'NUCLEAR REGULATORY COMMISSION', 'OFFICE OF PERSONNEL MANAGEMENT'
          ,'SMALL BUSINESS ADMINISTRATION', 'SOCIAL SECURITY ADMINISTRATION', 'STATE, DEPARTMENT OF'
          ,'TRANSPORTATION, DEPARTMENT OF', 'TREASURY, DEPARTMENT OF THE', 'VETERANS AFFAIRS, DEPARTMENT OF']
state_select=['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut',
    'Delaware','District of Columbia','Florida','Georgia','Guam','Hawaii','Idaho','Illinois','Indiana',
    'Iowa','Kansas','Kentucky','Louisiana',
    'Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi',
    'Missouri','Montana','Nebraska','Nevada',
    'New Hampshire','New Jersey','New Mexico','New York',
    'North Carolina','North Dakota','Ohio','Oklahoma',
    'Oregon','Pennsylvania','Puerto Rico','Rhode Island','South Carolina','South Dakota',
    'Tennessee','Texas','Utah','Vermont','Virginia',
    'Washington','West Virginia','Wisconsin','Wyoming']
state_select=[x.upper() for x in state_select]
#%%
def get_vendors():
    # vendors=plds.filter((pl.col("TOTAL_SB_ACT_ELIGIBLE_DOLLARS")>0) & (pl.col("FY")<max_year)).select(
    #     vendorcols+geocols+buyercols+contractcols+["FY"]+[pl.col(dolcols).map(lambda x: x>0)]).with_columns(
    #         pl.col("VENDOR_ADDRESS_ZIP_CODE").str.slice(0,5).alias("zip")
    #     )
    # vendors=vendors.unique()

    # ZIP_match=pl.read_csv("ZIP_to_FIPS_Name_20230322.csv",columns=["FIPS","zip","County","state","bus_ratio","state_names"]
    #                     ,dtypes={'zip':pl.Utf8, 'FIPS':pl.Utf8}
    #                     ).sort(by="bus_ratio",descending=True
    #                     ).drop("bus_ratio").unique(subset="zip",keep="first").lazy()
    # vendors=vendors.join(ZIP_match,how="left",on="zip").drop(["VENDOR_ADDRESS_ZIP_CODE","zip"])

    # vendors=vendors.with_columns(
    #     pl.when(pl.col("FY")<=2021)
    #     .then(pl.col("VENDOR_DUNS_NUMBER"))
    #     .otherwise(pl.col("VENDOR_UEI"))
    #     .alias("VENDOR_ID")
    #     ).drop(["VENDOR_DUNS_NUMBER","VENDOR_UEI"])

    #     #set-asides
    # SBA_set_asides=["SBA","SBP","RSB", "8AN", "SDVOSBC" ,"8A", "HZC","WOSB","SDVOSBS","HZS","EDWOSB"
    #     ,"WOSBSS","ESB","HS3","EDWOSBSS"]
    # SBA_socio_asides=SBA_set_asides[3:]

    # vendors=vendors.with_columns(
    #     pl.when(pl.col('TYPE_OF_SET_ASIDE').is_in(SBA_socio_asides))
    #         .then(pl.col('TYPE_OF_SET_ASIDE'))
    #         .when(pl.col('IDV_TYPE_OF_SET_ASIDE').is_in(SBA_set_asides))
    #         .then(pl.col('IDV_TYPE_OF_SET_ASIDE'))
    #         .otherwise(pl.col('TYPE_OF_SET_ASIDE'))
    #         .map_dict(set_aside_dict)
    #         .alias("set_aside")
    # ).drop(['IDV_TYPE_OF_SET_ASIDE','TYPE_OF_SET_ASIDE'])
    # vendors=vendors.rename({"VENDOR_ADDRESS_STATE_NAME":"State","state":"state_abbr","FUNDING_DEPARTMENT_NAME":"Department"
    #                             ,"FUNDING_AGENCY_NAME":"Agency","PRINCIPAL_NAICS_CODE":"NAICS"
    #                             ,"CONGRESSIONAL_DISTRICT":"Congressional District"})
    # vendors=vendors.rename(vendor_dict)
    # return vendors
    return pl.scan_parquet("VendorData.parquet")
#%%
# vendors=get_vendors().collect()
# vendors.write_parquet("Data",row_group_size=1000000,use_pyarrow=True,compression="zstd",compression_level=22)

#%%
def get_counts(vendors,var):
    for x in newdolcols:
        vendors=vendors.with_columns(
            pl.when(pl.col(x)==True)
            .then(pl.col("VENDOR_ID"))
            .otherwise(pl.lit("@"))
            .alias(x)
        )
    counts=vendors.select(newdolcols+[var]).groupby(var,maintain_order=True).n_unique()
    counts_adj=counts.select([pl.col(var),pl.col(newdolcols).map(lambda x:x-1)]).collect().to_pandas().set_index(var)
    return counts_adj

#%%
@st.cache_data
def get_choices():
    # vendors=get_vendors().collect().to_pandas()
    # six_digit_NAICS=vendors["NAICS"].drop_duplicates().sort_values().dropna()
    # two_digit_NAICS=six_digit_NAICS.str.slice(0,2).drop_duplicates().dropna()

    # NAICS_select=pd.concat([
    #     two_digit_NAICS,six_digit_NAICS], ignore_index=True
    #     ).drop_duplicates().sort_values().to_list()

    # agency_select={}
    # for x in department_select:
    #     agency_list=vendors[vendors['Department']==x]["Agency"].drop_duplicates().sort_values().to_list()
    #     agency_select.update({x:agency_list})
    # county_select={}
    # for x in state_select:
    #     county_list=vendors.loc[vendors['State']==x]["County"].drop_duplicates().sort_values().to_list()
    #     county_select.update({x:county_list})
    # CD_select={}
    # for x in state_select:
    #     CD_list=vendors.loc[vendors['State']==x]["Congressional District"].drop_duplicates().sort_values().to_list()
    #     CD_select.update({x:CD_list})

    # choices=[NAICS_select,agency_select,county_select,CD_select]
    # return choices
    return json.load(open ('Vendorchoices.json', 'r'))
#%%
choices=get_choices()
#json.dump(choices,open('choices.json', 'w'))

NAICS_select, agency_select, county_select, CD_select=get_choices()
department_select=list(agency_select.keys())
state_select=list(county_select.keys())
set_aside_select=list(dict.fromkeys(set_aside_dict.values()))

#%%
#initial_display
vendors=get_vendors()
#vendors.collect().write_parquet("vendors.parquet")
#%%
# user input
keys = ["Department", "Agency","NAICS","Set Aside","State","County", "CD","map","year"]

st.title("SBA Vendor Counts")
st.caption ("Scroll to the bottom for a state-by-state map")
department=st.sidebar.selectbox(label="Department",options=["All"]+department_select,index=0, key=keys[0])
if department != 'All':
    agency=st.sidebar.selectbox(label="Agency",options=["All"]+agency_select[department], key=keys[1])
    vendors=vendors.filter(pl.col("Department")==department)
    if agency != 'All':
        vendors=vendors.filter(pl.col("Agency")==agency)
        
NAICS=st.sidebar.multiselect(label="NAICS",options=NAICS_select, key=keys[2])
NAICS_pick = [pick for pick in NAICS if len(pick)==6]
for i in NAICS:
        if len(i)<6:
            NAICS_pick.extend([x for x in NAICS_select if (len(x)==6) & (x.startswith(i))])

if len(NAICS_pick)>0:
    vendors=vendors.filter(pl.col("NAICS").is_in(NAICS_pick))

set_aside=st.sidebar.multiselect(label="Set Aside",options=set_aside_select, key=keys[3])
if len(set_aside)>0:
    vendors=vendors.filter(pl.col("set_aside").is_in(set_aside))

state=st.sidebar.multiselect(label="State",options=state_select, key=keys[4])
if len(state)>0:
    vendors=vendors.filter(pl.col("State").is_in(state))
if (len(state)==1):
    county=st.sidebar.multiselect(label="County",options=["All"]+county_select[state[0]],default="All", key=keys[5])
    try:
        if (len(county)>0) & (county[0]!="All"):
            vendors=vendors.filter(pl.col("County").is_in(county))
    except:pass
    CD=st.sidebar.multiselect(label="Congressional District",options=["All"]+CD_select[state[0]],default="All", key=keys[6])
    try:
        if (len(CD)>0) & (CD[0]!= "All"): 
            vendors=vendors.filter(pl.col("Congressional District").is_in(CD))
    except:pass

map_select=st.sidebar.selectbox(label="Map what type of vendor?",options=newdolcols,index=1, key=keys[7])
year=st.sidebar.slider(label="Map which Fiscal Year?",min_value=min_year, max_value=max_year,value=max_year, key=keys[8])
vendor_map=vendors.filter(pl.col("FY")==year)

def reset():
    for key in keys:
        st.session_state[key] = []
    st.session_state["Department"] = "All"
    st.session_state["map"] = newdolcols[1]
    st.session_state["year"] = max_year
    

st.sidebar.button('Reset', on_click=reset)

#%%
def get_count_map(vendors,col,var):
    for x in newdolcols:
        vendors=vendors.with_columns(
        pl.when(pl.col(x)==True)
        .then(pl.col("VENDOR_ID"))
        .otherwise(pl.lit("@"))
        .alias(x)
    )
    counts=vendors.select([col]+[var]).groupby(var).n_unique()
    counts_adj=counts.select([pl.col(var),pl.col(col).map(lambda x:x-1)]).collect().to_pandas().set_index(var)
    return counts_adj
#%%
#prepare table and plots

vendor_table=get_counts(vendors,"FY")
pal = ["#002e6d", "#cc0000", "#969696", "#007dbc", "#197e4e", "#f1c400"]
try:
    fig=px.line(vendor_table,x=vendor_table.index,y=vendor_table.columns
                ,    color_discrete_sequence=pal,labels={"FY":"Fiscal Year","value":"vendors","variable":""}
    )
except ValueError:
    fig = None    

# st.write(map_select)
# st.write(year)
map_table= get_count_map(vendor_map,map_select,"state_abbr").iloc[:,0]

fig2 = go.Figure(data=go.Choropleth(
    locations=map_table.index, # Spatial coordinates
    z = map_table.array, # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Portland',
    colorbar_title = "Vendors",
))

fig2.update_layout(
    geo_scope='usa',
)
#%%    

if fig:
    st.plotly_chart(fig)

st.table(vendor_table)

if fig2:
    st.subheader(f"State-by-state map of vendors for FY{str(year)[-2:]}")
    st.plotly_chart(fig2)

st.caption("""Source: SBA Small Business Goaling Reports, FY09-FY22. A vendor is a unique DUNS or UEI that received a positive obligation in the fiscal year.\n
Abbreviations: SDB - Small Disadvantaged Business, WOSB - Women-owned small business, HUBZone - Historically Underutilized Business Zone, SDVOSB - Service-disabled veteran-owned small business.\n
This report consider transactions on the Small Business Goaling Report, after applying scorecard exclusions. Except for "All Vendors," the report considers only vendors that received a positive obligation in the given scorecard category (e.g., HUBZone vendors consider only vendors that received positive obligations in the HUBZone scorecard category).""")
