#%%
import plotly.express as px
import pandas as pd

pd.options.plotting.backend = "plotly"

#%%
aggData = pd.read_pickle('agg_data.pkl')
aggData.head()

#%%
fig = px.line(aggData,x='Dt',y='Nivel')
fig.show()

# %%
