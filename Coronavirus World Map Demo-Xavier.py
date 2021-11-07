#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
recovered = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
deaths = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')


# In[3]:


confirmed.head()


# In[4]:


recovered.head()


# In[5]:


deaths.head()


# In[6]:


print(confirmed.shape)
print(recovered.shape)
print(deaths.shape)


# In[7]:


last_update = '11/5/21'

global_case_by_province = confirmed[['Province/State','Country/Region',last_update]]
global_case_by_province.head(5)


# In[8]:


## To correct data consistency by using pd.merge (due to the shape printed!!!!) 不对齐的表格会对应出现诡异的数据
China_confirmed = confirmed[['Province/State',last_update]][confirmed['Country/Region'] == 'China']
China_confirmed = China_confirmed.rename(columns = {last_update:'confirmed'})
China_recovered = recovered[['Province/State',last_update]][recovered['Country/Region'] =='China']
China_recovered = China_recovered.rename(columns = {last_update:'recovered'})    
China_deaths = deaths[['Province/State',last_update]][deaths['Country/Region'] =='China']
China_deaths = China_deaths.rename(columns = {last_update:'deaths'})

_China_cases = pd.merge(China_confirmed, China_recovered, on='Province/State')
China_cases = pd.merge(_China_cases, China_deaths,on='Province/State')
China_cases = China_cases.set_index('Province/State')


# In[9]:


China_cases.head(34)


# In[10]:


others_confirmed = confirmed[['Country/Region',last_update]][confirmed['Country/Region'] != 'China']
others_confirmed = others_confirmed.groupby('Country/Region').sum()
others_confirmed = others_confirmed.rename(columns = {last_update:'confirmed'})

others_recovered = recovered[['Country/Region',last_update]][recovered['Country/Region'] != 'China']
others_recovered = others_recovered.groupby('Country/Region').sum()
others_recovered = others_recovered.rename(columns = {last_update:'recovered'})

others_deaths = deaths[['Country/Region',last_update]][confirmed['Country/Region'] != 'China']
others_deaths = others_deaths.groupby('Country/Region').sum()
others_deaths = others_deaths.rename(columns = {last_update:'deaths'})

#再次使用强大的pd.merge
_others = pd.merge(others_confirmed, others_recovered, on='Country/Region')
others = pd.merge(_others, others_deaths, on='Country/Region')
others.head(50)


# In[11]:


print(others.shape)


# In[12]:


locations = confirmed[['Country/Region','Lat','Long']]
locations = locations.groupby('Country/Region').mean()

locations.head(5)


# In[13]:


other_countries = pd.merge(others, locations, on='Country/Region')
other_countries.head()


# In[14]:


other_countries.loc['China'] = [China_cases['confirmed'].sum(),China_cases['recovered'].sum(),China_cases['deaths'].sum(),30.9756,112.2707]
other_countries.head(185)


# In[15]:


other_countries = other_countries.reset_index()
other_countries.head()


# In[16]:


import folium


# In[17]:


world_map = folium.Map(location=[10, -20], zoom_start=2.3,tiles='Stamen Toner')
for lat, lon, value, name in zip(other_countries['Lat'], other_countries['Long'], 
                                 other_countries['confirmed'], other_countries['Country/Region']):
    folium.CircleMarker([lat, lon],
                            radius=10,
                            popup = ('<strong>Country</strong>: ' + str(name).capitalize() + '<br>'                                
                            '<strong>Confirmed Cases</strong>: ' + str(value) + '<br>'),                        
                            color='red',                                                
                            fill_color='red',                        
                            fill_opacity=0.7 ).add_to(world_map)


# In[18]:


world_map


# In[19]:


import plotly.express as px


# In[20]:


confirmed.head()


# In[21]:


confirmed = confirmed.melt(id_vars = ['Province/State','Country/Region','Lat','Long'],
                          var_name='date',value_name = 'confirmed')
confirmed.head()


# In[22]:


confirmed['date_dt'] = pd.to_datetime(confirmed.date, format="%m/%d/%y")
confirmed.date = confirmed.date_dt.dt.date
confirmed.rename(columns={'Country/Region': 'country', 'Province/State': 'province'}, inplace=True)


# In[23]:


confirmed.head(5)


# In[24]:


recovered = recovered.melt(id_vars = ['Province/State', 'Country/Region', 'Lat', 'Long'], 
                           var_name='date',value_name = 'recovered')
recovered['date_dt'] = pd.to_datetime(recovered.date, format="%m/%d/%y")
recovered.date = recovered.date_dt.dt.date
recovered.rename(columns={'Country/Region': 'country', 'Province/State': 'province'}, inplace=True)
recovered.head()


# In[25]:


deaths = deaths.melt(id_vars = ['Province/State', 'Country/Region', 'Lat', 'Long'], var_name='date', value_name = 'deaths')
deaths['date_dt'] = pd.to_datetime(deaths.date, format="%m/%d/%y")
deaths.date = deaths.date_dt.dt.date
deaths.rename(columns={'Country/Region': 'country', 'Province/State': 'province'}, inplace=True)
deaths.head()


# In[26]:


merge_on = ['province', 'country', 'date']
all_data = confirmed.merge(deaths[merge_on + ['deaths']], how='left', on=merge_on).                         merge(recovered[merge_on + ['recovered']], how='left', on=merge_on)


# In[27]:


all_data.head(340)


# In[28]:


Coronavirus_map = all_data.groupby(['date_dt', 'province'])['confirmed', 'deaths','recovered', 'Lat', 'Long'].max().reset_index()
Coronavirus_map['size'] = Coronavirus_map.confirmed.pow(0.5)  # 创建实心圆大小
Coronavirus_map['date_dt'] = Coronavirus_map['date_dt'].dt.strftime('%Y-%m-%d')


# In[29]:


Coronavirus_map = Coronavirus_map.fillna(0)
Coronavirus_map.head()


# In[30]:


fig = px.scatter_geo(Coronavirus_map, lat='Lat', lon='Long', scope='world',
                     color='size',size='size',
                     hover_name='province',hover_data=['confirmed','deaths','recovered'],
                     projection="natural earth",animation_frame="date_dt",title='Coronavirus NB Map')
fig.update(layout_coloraxis_showscale=True)


# In[31]:


fig.show("notebook")
plotly.offline.plot(fig,filename = 'Coronavirus NB Map.html', auto_open=True)

