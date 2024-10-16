import pandas as pd

data = pd.read_csv('./output.tsv', sep='\t')

colors = pd.read_csv('./colors2.tsv', sep='\t')

no_color = {}
color = {}

# Ensure 'Color' column is of type object (string)
data['Color'] = data['Color'].astype('object')

print(data['Lineage'].unique())
print(colors['Label'].unique())

# lineages have * appended

for i in range(len(data)):
    lineage = data['Lineage'][i].replace('*', '')
    # is there a color for this lineage?
    if lineage in colors['Label'].values:
        # yes, add color to data
        color_value = colors[colors['Label'] == lineage]['Color'].values[0]
        data.at[i, 'Color'] = color_value
        color[data['Lineage'][i]] = color_value
    else:
        # no, add to set
        no_color[data['Lineage'][i]] = True

# print entries without color
print('No color for:')
print(no_color.keys())

# print entries with color
print('Color for:')
print(color.keys())

data.to_csv('./output_with_colors.tsv', sep='\t', index=False)

# create a table with all lineages and their colors, N/A if no color
lineage_colors = pd.DataFrame(columns=['Lineage', 'Color'])
for lineage in data['Lineage'].unique():
    if lineage in color:
        # no appending in pandas 2.0.0
        lineage_colors = pd.concat([lineage_colors, pd.DataFrame([[lineage, color[lineage]]], columns=['Lineage', 'Color'])])
    else:
        lineage_colors = pd.concat([lineage_colors, pd.DataFrame([[lineage, 'N/A']], columns=['Lineage', 'Color'])])

lineage_colors.to_csv('./lineage_colors.tsv', sep='\t', index=False)