
import csv


# Function to parse the CSV file and extract BOM information
def parse_octopart_bom(bom_file_path):
    bom_data = []

    try:
        with open(bom_file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header1 = next(reader)
            header2 = next(reader)

            # Combine the two header rows
            combined_header = [f'{h1} {h2}' if h2 else h1 for h1, h2 in zip(header1, header2)]

            for row in csv.DictReader(csvfile, fieldnames=combined_header):
                manufacturer = row.get('Manufacturer')
                part_number = row.get('MPN')
                description = row.get('Description')
                schemtic_ref = row.get('Schematic Reference')
                url = row.get('Octopart URL')
                digikey_part_number = row.get('SKU Digi-Key')
                mouser_part_number = row.get('SKU Mouser')

                if part_number and schemtic_ref:
                    bom_data.append({
                        'Part Number': part_number,
                        'Quantity': len(schemtic_ref.split(',')),
                        'Schematic Ref': schemtic_ref.split(','),
                        'Description': description,
                        'URL': url,
                        'Manufacturer': manufacturer,
                        'Digi-Key': digikey_part_number,
                        'Mouser': mouser_part_number,
                    })
                else:
                    print(f"Skipping row without Part Number or schemtic ref: {row}")
    except FileNotFoundError:
        print(f"File not found: {bom_file_path}")

    return bom_data
