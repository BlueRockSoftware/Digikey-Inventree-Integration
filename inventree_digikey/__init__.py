from .Digikey import get_order_from_order_number, get_part_from_part_number, get_order_history
from .Inventree import add_digikey_part, add_digikey_order, find_part, find_digikey_part, add_bom_line_item
from .Octopart import parse_octopart_bom


# Find part in Digikey and import it into inventree
def import_digikey_part(partnum: str, prompt=False):
    dkpart = get_part_from_part_number(partnum, prompt)
    return add_digikey_part(dkpart)


def import_digikey_order(order_number: str):
    dkorder = get_order_from_order_number(order_number)
    print(dkorder.order_number)
    for line_item in dkorder.line_items:
        print(line_item.digi_key_part_number)
    return add_digikey_order(dkorder, import_digikey_part)


def import_octopart_bom(bom_file_path, part_name):
    bom_data = parse_octopart_bom(bom_file_path)
    bom_part = find_part(part_name)
    print(f"BOM Part Number: {bom_part.name}, Part Number: {bom_part.pk}")

    dropped = []
    for component in bom_data:
        part = find_digikey_part(component['Digi-Key'])
        if part is not None:
            print(f"Part Number: {component['Part Number']}, Quantity: {component['Quantity']}, Ref: {component['Schematic Ref']}")
            print(f"Found Part Number: {part.name}, Part Number: {part.pk}")
            add_bom_line_item(bom_part, component['Quantity'], component['Schematic Ref'], part)
        else:
            print(f"ERROR: Missing Part Number: {component['Part Number']}, Digi-Key Part Number: {component['Digi-Key']}")
            if len(component['Digi-Key']) > 0:
                import_digikey_part(component['Digi-Key'])
                part = find_digikey_part(component['Digi-Key'])
                add_bom_line_item(bom_part, component['Quantity'], component['Schematic Ref'], part)
            else:
                print(f"ERROR: Could not find part {component['Part Number']}")
                dropped.append(component['Part Number'])

    for part in dropped:
        print(f"ERROR: Could not find part {part} in digikey, these parts on not imported in BOM")


def import_order_history():
    get_order_history("2021-01-01", "2023-12-31")