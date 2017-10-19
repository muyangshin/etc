from requests import get


def download_csvs():
    for i in range(1990, 2016):
        with open('qcew/by_area/annual/{0}.zip'.format(i), 'wb') as file:
            response = get('https://www.bls.gov/cew/data/files/{0}/csv/{0}_annual_by_area.zip'
                           .format(i))
            file.write(response.content)

download_csvs()