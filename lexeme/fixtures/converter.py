import csv
import json

csvfile = open('zipcodes.at.csv', 'r',encoding="UTF8")
jsonfile = open('addresses.json', 'w',encoding="UTF8")

fieldnames = ("country_code", "zipcode", "place", "state", "state_code",
              "province", "province_code", "community", "community_code", "latitude", "longitude")
reader = csv.DictReader(csvfile, fieldnames)
i = 1
jsonfile.write('[')
for row in reader:
    dict1 = {
        'model': 'lexeme.address',
        'pk': i,
        'fields': row
    }
    i = i + 1
    json.dump(dict1, jsonfile, ensure_ascii=False)

    jsonfile.write(',\n')
jsonfile.write(']')
