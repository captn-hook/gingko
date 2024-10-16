import pandas as pd
import urllib
import requests

#data is currently in ./data.tsv

data = pd.read_csv('./2024_oct_16_q_data.csv', sep=',')

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
#DATE,FLIGHT_COUNTRY_OF_ORIGIN,LINEAGE,Highlight Color,City name

localities = data['FLIGHT_COUNTRY_OF_ORIGIN'].tolist()
dates = data['DATE'].tolist()

dates = datesToInteger(dates)

output_df = pd.DataFrame(columns=['Date', 'Latitude', 'Longitude', 'City', 'Country', 'Lineage', 'Color'])

output_df['Date'] = data['DATE'].apply(lambda x: dates[x])
#output_df['City'] = data['City name']
output_df['Country'] = data['FLIGHT_COUNTRY_OF_ORIGIN']
output_df['Lineage'] = data['LINEAGE']
#output_df['Color'] = data['Highlight Color']
output_df['Airport'] = data['Airport']

issues = []
#output_df['Location'] = localities.apply(lambda x: [i.strip() for i in x.split('/') if i][-1])
# Create a dictionary to store queried locations
queried_locations = {}

headers = {
    'User-Agent': 'my map tool'
}

for i in range(len(localities)):
    query = data['FLIGHT_COUNTRY_OF_ORIGIN'][i] + ' Airport'
    if query in queried_locations:
        output_df.loc[i, 'Latitude'] = queried_locations[query]['lat']
        output_df.loc[i, 'Longitude'] = queried_locations[query]['lon']
    else:
        url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(query) + '&format=json'
        response = requests.get(url, headers=headers)
        
        # print(f"Query: {query}")
        # print(f"Status Code: {response.status_code}")
        # print(f"Response Text: {response.text}")

        if response.status_code == 200:
            try:
                response_json = response.json()
                if response_json:
                    queried_locations[query] = {'lat': response_json[0]['lat'], 'lon': response_json[0]['lon']}
                    output_df.loc[i, 'Latitude'] = response_json[0]['lat']
                    output_df.loc[i, 'Longitude'] = response_json[0]['lon']
                else:
                    issues.append([i, data['FLIGHT_COUNTRY_OF_ORIGIN'][i]])
            except ValueError:
                issues.append([i, data['FLIGHT_COUNTRY_OF_ORIGIN'][i]])
        else:
            issues.append([i, data['FLIGHT_COUNTRY_OF_ORIGIN'][i]])

print(issues)

for issue in issues:
    i, location = issue

    url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(location) + '&format=json'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            response_json = response.json()
            if response_json:
                queried_locations[location] = {'lat': response_json[0]['lat'], 'lon': response_json[0]['lon']}
                output_df.loc[i, 'Latitude'] = response_json[0]['lat']
                output_df.loc[i, 'Longitude'] = response_json[0]['lon']
            else:
               print(f"Could not find location: {location}")    
        except ValueError:
            print(f"Could not find location: {location}")
    else:
        print(f"Could not find location: {location}")

output_df.to_csv('output.tsv', sep='\t', index=False)