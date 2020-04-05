import pandas as pd
csv = pd.read_csv("04-04-2020.csv")
csv = csv.sort_values(["Deaths"], ascending=[False])
print(csv)