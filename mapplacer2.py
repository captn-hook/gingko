import pandas as pd
import urllib
import requests

#data is currently in ./data.tsv

data = pd.read_csv('./data3.csv', sep=',')

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
#COLLECTION_DATE,FLIGHT_COUNTRY_OF_ORIGIN,LINEAGE,Highlight Color,City name

localities = data['FLIGHT_COUNTRY_OF_ORIGIN'].tolist()
dates = data['COLLECTION_DATE'].tolist()

dates = datesToInteger(dates)

output_df = pd.DataFrame(columns=['Date', 'Latitude', 'Longitude', 'City', 'Country', 'Lineage', 'Color'])

output_df['Date'] = data['COLLECTION_DATE'].apply(lambda x: dates[x])
output_df['City'] = data['City name']
output_df['Country'] = data['FLIGHT_COUNTRY_OF_ORIGIN']
output_df['Lineage'] = data['LINEAGE']
output_df['Color'] = data['Highlight Color']

issues = []
#output_df['Location'] = localities.apply(lambda x: [i.strip() for i in x.split('/') if i][-1])
# Create a dictionary to store queried locations
queried_locations = {}
for i in range(len(localities)):
    
    #query like 'City name, FLIGHT_COUNTRY_OF_ORIGIN'
    query = data['City name'][i] + ', ' + data['FLIGHT_COUNTRY_OF_ORIGIN'][i]
    # Check if the location has already been queried
    if query in queried_locations:
        output_df.loc[i, 'Latitude'] = queried_locations[query]['lat']
        output_df.loc[i, 'Longitude'] = queried_locations[query]['lon']
    else:
                
        url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(query) + '&format=json'
        #url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(query + ' Airport') + '&format=json'
        response = requests.get(url).json()

        if response:
            queried_locations[query] = {'lat': response[0]['lat'], 'lon': response[0]['lon']}
            output_df.loc[i, 'Latitude'] = response[0]['lat']
            output_df.loc[i, 'Longitude'] = response[0]['lon']
            
        else:
            print('No results found for query: ' + query)
        
            queried_locations[query] = {'lat': 'N/A', 'lon': 'N/A'}

output_df.to_csv('output3.tsv', sep='\t', index=False)