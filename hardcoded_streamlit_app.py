import datetime
import pandas as pd
import streamlit as st
import numpy as np
from numpy import datetime64
import xlrd


"""
# Fuel Cost Dashboard
"""
#altair https://github.com/streamlit/example-app-commenting/
# Give the location of the file

#uploaded_file = st.file_uploader("Choose a XLS file", type="xls")
#if uploaded_file:
xls_file = "PET_PRI_SPT_S1_D.xls"
df = pd.read_excel(xls_file)

xls = pd.ExcelFile(xls_file)
df_crude_oil = pd.read_excel(xls, 'Data 1')
df_conv_gas = pd.read_excel(xls, 'Data 2')
df_reg_gas = pd.read_excel(xls, 'Data 3')
df_heating_oil = pd.read_excel(xls, 'Data 4')
df_diesel_fuel = pd.read_excel(xls, 'Data 5')
df_kerosene= pd.read_excel(xls, 'Data 6')
df_propane = pd.read_excel(xls, 'Data 7')

us_crude_label = 'Oil price $, US Cushing OK'
euro_crude_label = 'Oil price $, Europe'
newyork_conv_label = 'Conv. gase $, US NY'
gulf_kersone_label = 'Kerosene $, US Gulf Coast'

st.sidebar.header("Fuel Type Filters:")

df_crude_oil_graph = pd.DataFrame({'date': df_crude_oil.iloc[2:,0]})

oil_types = st.sidebar.multiselect(
    "Select the Fuel Types:",
    options=[us_crude_label,  euro_crude_label,newyork_conv_label,gulf_kersone_label],
    default=[us_crude_label,  euro_crude_label],
)


if us_crude_label in oil_types:
    df_crude_oil_graph[us_crude_label] =df_crude_oil.iloc[2:,1]
 
if euro_crude_label in oil_types:
    df_crude_oil_graph[euro_crude_label] =df_crude_oil.iloc[2:,2]

#https://stackoverflow.com/questions/17134716/convert-dataframe-column-type-from-string-to-datetime
df_crude_oil_graph['date'] = pd.to_datetime(df_crude_oil_graph['date'])
df_crude_oil_graph = df_crude_oil_graph.set_index('date')


if newyork_conv_label in oil_types:
  df_conv_gas = pd.DataFrame({'date': df_conv_gas.iloc[3:,0], newyork_conv_label:df_conv_gas.iloc[3:,1]})
  df_conv_gas['date'] = pd.to_datetime(df_conv_gas['date'])
  df_crude_oil_graph = df_crude_oil_graph.merge(df_conv_gas, how='left', on='date')
  df_crude_oil_graph = df_crude_oil_graph.set_index('date')  
  
if gulf_kersone_label in oil_types:
  df_kerosene = pd.DataFrame({'date': df_kerosene.iloc[3:,0], gulf_kersone_label:df_kerosene.iloc[3:,1]})
  df_kerosene['date'] = pd.to_datetime(df_kerosene['date'])
  df_crude_oil_graph = df_crude_oil_graph.merge(df_kerosene, how='left', on='date')
  df_crude_oil_graph = df_crude_oil_graph.set_index('date')  


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
   

df_selection = df_crude_oil_graph.query(
    "date >= @start_date & date <= @end_date"
)

left_column, middle_column, right_column = st.columns(3)

if oil_types:
  with left_column:
      st.subheader("Average")
      for fuel_type in oil_types:
          st.write(fuel_type + ":" + str(np.round(df_selection[fuel_type].mean(),2)))
  with middle_column:
     st.subheader("Maximum:")
     for fuel_type in oil_types:
          st.write(fuel_type + ":" + str(np.round(df_selection[fuel_type].max(),2)))
  with right_column:
    st.subheader("Minimum")
    for fuel_type in oil_types:
          st.write(fuel_type + ":" + str(np.round(df_selection[fuel_type].min(),2)))
else:
    st.subheader("No Fuel Types Selected")

st.line_chart(df_selection)

sf_sort = df_selection.sort_values("date", axis = 0, ascending = False)
st.dataframe(sf_sort)



# Get Examples in Excel https://docs.microsoft.com/en-us/power-bi/create-reports/sample-datasets#explore-excel-samples-in-excel
# This is from a consulting company that has real anonymized data.
