import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv('dynamic_pricing_output.csv')

# Step 1: Simulate order dates
df['date'] = pd.date_range(start='2025-07-01', periods=len(df))

# Step 2: Aggregate daily demand (total Load_ton per day)
daily_demand = df.groupby('date')['Load_ton'].sum().reset_index()

# Prepare data for Prophet
daily_demand = daily_demand.rename(columns={'date': 'ds', 'Load_ton': 'y'})

# Step 3: Initialize Prophet model
model = Prophet()

# Step 4: Fit model
model.fit(daily_demand)

# Step 5: Create future dataframe for next 7 days
future = model.make_future_dataframe(periods=7)

# Step 6: Predict future demand
forecast = model.predict(future)

# Step 7: Plot forecast
model.plot(forecast)
plt.title('7-Day Load Demand Forecast')
plt.xlabel('Date')
plt.ylabel('Load (tons)')
plt.show()

# Step 8: Print forecasted demand for next 7 days
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7))
