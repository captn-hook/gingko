import pandas as pd
import urllib
import requests

#data is currently in ./data.tsv

data = pd.read_csv('./data.tsv', sep='\t')

#print headers
#print(data.columns)

def datesToInteger(dates):
    #converts a range of dates to range of integers
    #and returns dictionary to relate the two
    #date format: 2020-12-12
    #de duplicate
    deDupedDates = list(set(dates))
    deDupedDates.sort()

    dateDict = {}
    for i in range(len(deDupedDates)):
        dateDict[deDupedDates[i]] = i

    return dateDict


#we want the lat and long of each location from the location column

localities = data['Location'].tolist()
dates = data['Collection date'].tolist()

dates = datesToInteger(dates)

#format of column is Region / Country / State / City / County / Airport, where everything after state is optional
# Example: North America / USA / California / San Mateo County / San Francisco International Airport
#we want the lat and long of our best guess airport for each location

output_df = pd.DataFrame(columns=['Collection date', 'Region', 'Country', 'State', 'City', 'County', 'Airport', 'Latitude', 'Longitude'])

#output_df['Location'] = localities.apply(lambda x: [i.strip() for i in x.split('/') if i][-1])
# Create a dictionary to store queried locations
queried_locations = {}
for i in range(len(localities)):

    locality_parts = localities[i].split('/')
    locality_parts_len = len(locality_parts)

    output_df.loc[i, 'Collection date'] = dates[data['Collection date'][i]]
    output_df.loc[i, 'Region'] = locality_parts[0].strip()
    output_df.loc[i, 'Country'] = locality_parts[1].strip()
    output_df.loc[i, 'State'] = locality_parts[2].strip()
    output_df.loc[i, 'City'] = locality_parts[3].strip() if locality_parts_len > 3 else ''
    output_df.loc[i, 'County'] = locality_parts[4].strip() if locality_parts_len > 4 else ''
    
    output_df.loc[i, 'Airport'] = locality_parts[-1].strip() if locality_parts_len > 5 else ''

    #data = data.dropna(subset=['Location']).reset_index(drop=True)
    outairI = output_df['Airport'][i]
    outcityI = output_df['City'][i]
    outstateI = output_df['State'][i]

    query = outairI if outairI else outcityI + ", " + outstateI if outcityI else outstateI
    query += ' Airport' if 'Airport' not in query else ''
    
    # Check if the location has already been queried
    if query in queried_locations:
        output_df['Latitude'][i] = queried_locations[query]['lat']
        output_df['Longitude'][i] = queried_locations[query]['lon']
    else:
        url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(query) + '&format=json'
        response = requests.get(url).json()

        if response:
            output_df['Latitude'][i] = response[0]['lat']
            output_df['Longitude'][i] = response[0]['lon']

            # Store the location in the dictionary
            queried_locations[query] = {'lat': response[0]['lat'], 'lon': response[0]['lon']}
        else:
            print('No results found for query: ' + query)

output_df.to_csv('output.tsv', sep='\t', index=False)