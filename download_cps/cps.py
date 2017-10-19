import os
import re
import csv

from requests import get


def create_colnames(wd):
    this_regex = re.compile(r'_column\((\d+)\s+\)\s+([0-9a-z]+)\s([0-9a-z]+)(\s)')
    dict_type = {
        "str": "character",
        "byt": "integer",
        "int": "integer",
        "dou": "numeric",
        "lon": "numeric",
    }

    for file in os.listdir('{}/dct/'.format(wd)):
        var_names = []
        var_locs = []
        var_types = []

        with open('{0}/dct/{1}'.format(wd, file), newline='', encoding='utf-8') as dctfile:
            for line in dctfile:
                if line[:7] == '_column':
                    this_search = this_regex.search(line)
                    var_names.append(this_search.group(3))
                    var_locs.append(this_search.group(1))
                    var_types.append(dict_type[this_search.group(2)[:3]])

        with open('{0}/colnames/{1}.csv'.format(wd, file), 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for index, value in enumerate(var_names):
                if index != len(var_names) - 1:
                    writer.writerow([value, int(var_locs[index+1]) - int(var_locs[index]), var_types[index]])
                else:
                    writer.writerow([value, 15, var_types[index]])


def download_basic_monthly(wd, year):
    for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']:
        with open('{0}/dat/zip/{1}{2}pub.zip'.format(wd, month, year), 'wb') as file:
            response = get('http://www.nber.org/cps-basic/{0}{1}pub.zip'
                           .format(month, year))
            file.write(response.content)

wd = 'C:/research/CPS/data'
create_colnames(wd)
download_basic_monthly(wd, "07")
