import pandas as pd

data = pd.read_csv("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output_with_colors4.tsv", sep='\t')

# how many rows have the same Date and Country?
x = data.groupby(['Date', 'Country']).size()

# change date to float
data['Date'] = data['Date'].astype(float)

# edit the dates on these rows
tracking = -1
for i, row in data.iterrows():
    if x[row['Date'], row['Country']] > 1 and tracking == -1:
        duplicate_num = x[row['Date'], row['Country']]
        tracking = duplicate_num - 1
    elif x[row['Date'], row['Country']] > 1:
        # add to the date of this row
        addend = 1 / (tracking + 1)
        data.at[i, 'Date'] += addend
        tracking -= 1
        if tracking == 0:
            tracking = -1

data.to_csv("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output_with_colors7s.tsv", sep='\t', index=False)