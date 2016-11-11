#!/usr/bin/env python

# Generate the SQL dump file from the postal code download

from ansible.module_utils.basic import AnsibleModule

db_name = "weather_db"


def fetchGeoData(src):
    data = list()

    try:
        lines = [line.rstrip('\n') for line in open(src, 'r')]
    except:
        return 0

    zipline = list()
    for line in lines:
        zipdata = line.split('\t')
        zipline = map(zipdata.__getitem__, [0, 1, 2, 3, 4, 5, 9, 10])
        data.append(zipline)

    return data


def generateDBData():
    db = "DROP DATABASE IF EXISTS `%s`;\n" % db_name
    db += "CREATE DATABASE `%s`;\nUSE `%s`;\n" % (db_name, db_name)
    return db


def generateTableData(geo_data):
    # 0 County, 1 Zip, 2 City, 3 State, 4 State Short,
    # 5 County, 9 Latitude, 10, Longitude
    line = ('CREATE TABLE zipcodes (country VARCHAR(2),'
            '                       zipcode VARCHAR(20),'
            '                       city VARCHAR(180),'
            '                       state VARCHAR(100),'
            '                       state_short VARCHAR(20),'
            '                       county VARCHAR(20),'
            '                       latitude VARCHAR(20),'
            '                       longitude VARCHAR(20));')
    for data in geo_data:
        line += "INSERT INTO zipcodes VALUES (\"%s\");\n" % '", "'.join(data)

    return line.rstrip('\n')


def generateGrantData(user):
    line = "GRANT ALL PRIVILEGES ON %s.zipcodes TO '%s'@'localhost';\n" \
           % (db_name, user)
    line += "FLUSH PRIVILEGES;\n"

    return line


def write_sql(sql_output_string, dest):
    try:
        with open(dest, "w") as f:
            f.write(sql_output_string)
    except:
        return 1

    return 0


def main():
    module = AnsibleModule(
        argument_spec = dict(
            dest=dict(default='/tmp/dump.sql'),
            src=dict(default=None),
            user=dict(default=None)
        )
    )

    db_data = generateDBData()
    geoData = fetchGeoData(module.params['src'])
    if not geoData:
        module.fail_json(msg="Failed to read Geodata file")

    table_data = generateTableData(geoData)
    grant_data = generateGrantData(module.params['user'])
    failed = write_sql("\n".join([db_data, table_data, grant_data]),
                       module.params['dest'])
    if failed:
        module.fail_json(msg="Failed to write output.")

    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
