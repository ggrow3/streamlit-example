import datetime
from doctest import master
import pandas as pd
import streamlit as st
import numpy as np
from numpy import datetime64
import xlrd


"""
# Fuel Cost Dashboard
"""
def get_data_frame(xls_file):
    xls = pd.ExcelFile(xls_file)
    sheets_dict = pd.read_excel(xls_file, sheet_name=None)
    master_df = None
    sheet_name = []
    for name, sheet in sheets_dict.items():
        excel_df = pd.read_excel(xls, name)
    
        if "Data" in name:
            sheet_name.append(excel_df.columns.values[1].split(':')[1].strip())
  
            key_dict = {}
            for i,value in enumerate(excel_df.iloc[1,:].values):
                key_dict[value] = list(excel_df.iloc[2:,i])
            
            df = pd.DataFrame(key_dict)
         
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
     
            if master_df is None:
                master_df = df
            else:
                master_df = pd.merge(master_df, df, how="outer", on="Date")
    return master_df

uploaded_file = st.sidebar.file_uploader("Choose a XLS file", type="xls")
#xls_file = "PET_PRI_SPT_S1_D.xls"
xls_file = uploaded_file

if uploaded_file is not None:
    master_df = get_data_frame(xls_file)
else:
    master_df = pd.DataFrame({'Date':[]})

st.sidebar.header("Fuel Type Filters:")


oil_types = st.sidebar.multiselect(
    "Select the Fuel Types:",
    options= master_df.columns.values
    #default= master_df.columns.values
)


col1, col2 = st.columns(2)

start_date_range = st.sidebar.radio(
     "What's your time range?",
     ( '5 years', '1 year', '3 months', '1 month', 'Custom Range'))
years = 0
days = 0
if start_date_range != 'Custom Range':
    if 'month' in start_date_range:
        days -= int(start_date_range[0]) * 30
        start_date = datetime.datetime.now() + datetime.timedelta(days)
    else:
        years -= int(start_date_range[0])
        days_per_year = 365.24
        start_date = datetime.datetime.now() + datetime.timedelta(days=(years*days_per_year))
    end_date = datetime.datetime.now()
else:
    with col1:
        years -= int(5)
        days_per_year = 365.24
        start_date_text = datetime.datetime.now() + datetime.timedelta(days=(years*days_per_year))
        start_date = st.sidebar.date_input(
        "Start Date",
        start_date_text)
   
    with col2:
        end_date = st.sidebar.date_input(
        "End Date",
      datetime.datetime.now())
   
df_selection = master_df.query(
    "Date >= @start_date & Date <= @end_date"
)

for col_name in master_df.columns.values:
  if col_name not in oil_types:
    df_selection.drop(col_name, axis=1, inplace=True)
       

left_column, middle_column, right_column = st.columns(3)

if oil_types:
  with left_column:
      st.subheader("Average Price")
      for fuel_type in oil_types:
        st.write(fuel_type + ":" + str(np.round(df_selection[fuel_type].mean(),2)))
  with middle_column:
     st.subheader("Maximum Price:")
     for fuel_type in oil_types:
         st.write(fuel_type + ":" + str(np.round(df_selection[fuel_type].max(),2)))
  with right_column:
    st.subheader("Minimum Price")
    for fuel_type in oil_types:
      st.write(fuel_type + ":" + str(np.round(df_selection[fuel_type].min(),2)))
else:
    st.subheader("No Fuel Types Selected")

st.line_chart(df_selection)

if uploaded_file is not None:
  sf_sort = df_selection.sort_values("Date", axis = 0, ascending = False)
  st.dataframe(sf_sort)  


# Get Examples in Excel https://docs.microsoft.com/en-us/power-bi/create-reports/sample-datasets#explore-excel-samples-in-excel
# This is from a consulting company that has real anonymized data.
