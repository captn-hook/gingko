import os
import csv
import matplotlib.pyplot as plt

def getData(path):
    sep = '\t'
    data = {}
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=sep)
        headers = next(reader)
        for h in headers:
            data[h] = []
        for row in reader:
            for i in range(len(row)):
                data[headers[i]].append(row[i])

    return data

def ls(path):
    return os.listdir(path)

data = getData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output.tsv")
for key in data:
    print(key, len(data[key]))


image = plt.imread("C:\\Users\\trist\\Desktop\\gingkoi\\D.png") #world map
#Collection date	Strain	Location	Latitude	Longitude

plt.imshow(image, extent=[-180, 180, -90, 90])

for i in range(len(data['Location'])):
    plt.plot(float(data['Longitude'][i]), float(data['Latitude'][i]), 'ro')
    plt.text(float(data['Longitude'][i]), float(data['Latitude'][i]), data['Location'][i], fontsize=8)

plt.show()