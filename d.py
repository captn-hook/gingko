import pandas as pd

data = pd.read_csv("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\2024_oct_16_q_data.csv", sep=',')
data2 = pd.read_csv("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output_with_colors3.tsv", sep='\t')

print("Columns in data:", data.columns)
print("Columns in data2:", data2.columns)

# get the dates in order
dates = data["DATE"].unique()
dates.sort()
print("Dates:", dates)

# create a mapping of dates to an integer starting from 1
date_map = {date: i+1 for i, date in enumerate(dates)}

print("Date map:", date_map)

# replace data2 "Date" column
# then replace that with the integer mapping
data2["Date"] = data["DATE"].map(date_map)

print(data2)

# save as out 4
data2.to_csv("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output_with_colors4.tsv", sep='\t', index=False)