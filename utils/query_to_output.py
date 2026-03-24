import io, csv

def query_to_json(query):
    if not query:
        return {}
    output = {}
    for item in query:
        prefix = item.prefix
        country_code = item.country_code
        region_code = item.region_code
        city = item.city
        postal_code = item.postal_code
        output[prefix] = {
            'country_code': country_code,
            'region_code': region_code,
            'city': city,
            'postal_code': postal_code
        }
    return output

def build_geofeed_csv(rows, include_header=True):
    output = io.StringIO()
    writer = csv.writer(output)

    if include_header:
        writer.writerow(["prefix", "country_code", "region_code", "city", "postal_code"])

    for row in rows:
        writer.writerow([
            row.prefix,
            row.country_code,
            row.region_code,
            row.city,
            row.postal_code
        ])

    csv_data = output.getvalue()
    output.close()
    return csv_data