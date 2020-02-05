import pandas as pd

excel_path = input().strip()

data = pd.read_csv(excel_path, header=0)

for i in data.itertuples():
    print(i)
    print(i.Genus.strip())