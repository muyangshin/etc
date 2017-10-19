import json
import requests
import csv
import os
import codecs


# fetch and save JSONs from starbucks, by zip codes
def fetch_json():
    zipcodes = []

    # load zipcodes
    with open('california zip codes.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            zipcodes.append(row[0])

    for index, zipcode in enumerate(zipcodes):
        url = 'https://www.starbucks.com/bff/locations?place={0}'.format(zipcodes[index])
        response = requests.get(url)
        data = json.loads(response.text)

        with open('json/{0}.txt'.format(zipcode), 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)

    # cities = []
    # counties = []
    #
    # # load city list
    # with open('california city list.csv', newline='') as csvfile:
    #     reader = csv.reader(csvfile, delimiter=',')
    #     for row in reader:
    #         cities.append(row[0])
    #         counties.append(row[1])
    # print(cities)
    # print(counties)
    #
    # # fetch json
    # for index, city in enumerate(cities):
    #     url = 'https://www.starbucks.com/bff/locations?place={0}, {1}'.format(cities[index], counties[index])
    #     response = requests.get(url)
    #     data = json.loads(response.text)
    #
    #     for store in data['stores']:
    #         if store['id'] not in stores:
    #             stores[store['id']] = store
    #
    #
    # for i in range(len(zipcodes) // 100):
    #     stores = {}
    #
    #     # fetch json
    #     for index, city in enumerate(zipcodes[0:100 * i]):
    #         url = 'https://www.starbucks.com/bff/locations?place={0}'.format(zipcodes[index])
    #         response = requests.get(url)
    #         data = json.loads(response.text)
    #
    #         if 'placeNameNotFound' not in data:
    #             for store in data['stores']:
    #                 stores[store['id']] = store
    #
    #     # write output
    #     with open('starbucks california.csv.', 'a', newline='', encoding='utf-8') as csvfile:
    #         writer = csv.writer(csvfile, delimiter=',')
    #         for key, store in stores.items():
    #             if len(store['addressLines']) == 2:
    #                 writer.writerow([
    #                     i,
    #                     key,
    #                     store['addressLines'][0],
    #                     '',
    #                     store['addressLines'][1],
    #                     store['coordinates']['latitude'],
    #                     store['coordinates']['longitude']
    #                 ])
    #             else:
    #                 writer.writerow([
    #                     i,
    #                     key,
    #                     store['addressLines'][0],
    #                     store['addressLines'][1],
    #                     store['addressLines'][2],
    #                     store['coordinates']['latitude'],
    #                     store['coordinates']['longitude']
    #                 ])


def parse_jsons():
    stores = {}     # id: store

    for file in os.listdir('json/'):
        data = json.load(codecs.open('json/{0}'.format(file), 'r', 'utf-8-sig'))

        if not data['paging']['total'] == 0:
            for store in data['stores']:
                stores[store['id']] = store

    # print output
    os.remove('starbucks california.csv')
    with open('starbucks california.csv.', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for key, store in stores.items():
            if len(store['addressLines']) == 2:
                writer.writerow([key, store['addressLines'][0], '', store['addressLines'][1], store['coordinates']['latitude'],
                                 store['coordinates']['longitude']])
            elif len(store['addressLines']) == 3:
                writer.writerow([key, store['addressLines'][0], store['addressLines'][1], store['addressLines'][2], store['coordinates']['latitude'],
                                 store['coordinates']['longitude']])
            else:
                writer.writerow([key, store['addressLines'][0], '', '', store['coordinates']['latitude'], store['coordinates']['longitude']])
