import pandas as pd
import urllib.request

print("04-04-2020")
originalData = pd.read_csv(f'04-04-2020.csv')
data = originalData[['Country_Region', 'Confirmed', 'Deaths', 'Recovered', 'Active']]
combinedData = data.groupby('Country_Region').sum()
combinedData = combinedData.sort_values(["Confirmed"], ascending=[False])
print(combinedData)