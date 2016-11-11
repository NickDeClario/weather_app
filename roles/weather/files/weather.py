#!/usr/bin/env python

import cgi
import cgitb; cgitb.enable()
import _mysql
import MySQLdb as mdb
import json
import os
import pprint
import re
import requests
from time import gmtime, strftime

header = '''Content-Type: text/html\n\n
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1"
 http-equiv="content-type">
  <title>Weather Report</title>
  <link rel="stylesheet" href="style.css" type="text/css" />
</head>
'''

# noaa.gov API URL:
# http://forecast.weather.gov/MapClick.php?lat=<LAT>&lon=<LON>&FcstType=json


def formatWeather(data):
    if data.get('success') == False:
        content = '<div class="failure"><font color=red>%s</font></div>' % data['message']
        return content

    content = '<table><tr><td>'
    content += '<div class="location">Weather for %s</div>\n' % data['productionCenter']
    content += '<div class="date">Generated on %s</div>\n' % data['creationDate']

    if len(data['data']['hazard']) > 0:
        content += "<div class=\"Hazard\"><font color=red>Hazard Alert(s)</font><br /><ul>\n"
        for index in range(0, len(data['data']['hazard'])):
            content += "<li><a href=\"%s\">%s</a></li>\n" % (data['data']['hazardUrl'][index], data['data']['hazard'][index])
        content += "</ul></div><br />\n"

    if len(data['currentobservation']) > 0:
        content += '<div class="currentWeatherImg"><img src="http://forecast.weather.gov/newimages/medium/%s"></div>\n' % data['currentobservation']['Weatherimage']
        content += '<div class="currentWeatherTemp">%s %s&deg;</div>\n' % (data['currentobservation']['Weather'], data['currentobservation']['Temp'])
        content += '<div class="currentLocation">%s, %s</div>\n' % (data['currentobservation']['name'], data['currentobservation']['state'])

    content += '</td></tr></table>'

    return content


def formatSearch():
    content = '''
<table><tr><td>
<div class="SearchTitle">Search Zip, City or State for Current Weather</div>
<form>
    <div class="formText">Postal Code <input type=text name="zipcode"></div>
    <div class="formOr">or</div>
    <div class="formText">City <input type=text name="city"></div>
    <div class="formText">State<input type=text name="state"></div>
    <div class="formSubmit"><input type="submit" name="submit" value="Search">
</form>
</td></tr></table>
'''

    return content


def formatResults(data):
    content = "Multiple search results; choose location:"
    content += "<ul>\n"

    url = re.sub(r"\?zip.*$", "", os.environ['HTTP_REFERER'])
    for result in data:
        content += '<li><a href="%s?zipcode=%s">%s - %s, %s</a></li>\n' % (url, result[1], result[1], result[2], result[3])
    content += "</ul>"

    return content


def formatSearchFailure(data):
    content = "Unable to find location"

    return content

def fetchFormValues():
    form = cgi.FieldStorage()
    data = dict({'state_short': None})
    fields = ('zipcode', 'city', 'state')
    for field in fields:
        data[field] = None
        value = form.getvalue(field, None)
        if field == 'state' and value:
            if len(value) == 2:
                data['state_short'] = value
                data[field] = None
            else:
                data[field] = value
                data['state_short'] = None
        elif value:
            data[field] = value

    return data


def genSqlSearch(args):
    search = "SELECT * FROM zipcodes "

    if args['zipcode'] is not None:
        return "%s WHERE zipcode LIKE '%%%s%%';" % (search, args['zipcode'])

    more = None
    if args['state'] is not None:
        search += "WHERE state LIKE '%%%s%%' " % args['state']
        more = 1
    if args['state_short'] is not None:
        if more:
            search += "AND "
        else:
            search += "WHERE "
        search += "state_short LIKE '%%%s%%' " % args['state_short']
        more = 1

    if args['city'] is not None:
        if more:
            search += "AND "
        else:
            search += "WHERE "
        search += "city LIKE '%%%s%%'" % args['city']
        more = 1

    search += ";"
    return search


def searchLocations(params):
    results = list()

    if len(params) > 0:
        search = genSqlSearch(params)

        try:
            conn = mdb.connect('localhost', 'weather_user', '', 'weather_db')
            cur = conn.cursor()
            cur.execute(search)
            for row in cur.fetchall():
                results.append(row)

        except:
            return ['<font color="red"><b>Failure to connect to DB</b></font>']

        if conn:
            conn.close()

    return results


def fetchWeather(data):
    url = "http://forecast.weather.gov/MapClick.php?lat=%s&lon=%s&FcstType=json" % (data[6], data[7])
    response = requests.get(url)

    return json.loads(response.content)


def main():

    print header

    incoming = fetchFormValues()
    search_results = searchLocations(incoming)

    if len(incoming) <= 0:
        print formatSearch()
    elif len(search_results) > 1:
        print formatResults(search_results)
        print formatSearch()
    elif len(search_results) == 1:
        weather_json = fetchWeather(search_results[0])
        print formatSearch()
        print formatWeather(weather_json)
    else:
        print formatSearchFailure(incoming)
        print formatSearch()


if __name__ == '__main__':
    main()
