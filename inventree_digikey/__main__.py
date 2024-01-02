from . import import_digikey_part, import_digikey_order, import_octopart_bom, import_order_history
import sys
import argparse

parser = argparse.ArgumentParser(description='Import Digikey part numbers into InvenTree')

# Add an optional '-y' flag to bypass prompting
parser.add_argument('-y', action='store_true', help='Bypass user prompts and assume "yes"')
parser.add_argument('-o', action='store_true', help='Query and Order number and import it')
parser.add_argument('-b', '--bom', type=str, help='Path to Octopart BOM file')
parser.add_argument('-l', '--history', action='store_true', help='Get order history')

# Add the 'part_number', 'part_name' or 'order id' argument as the last item on the command line
parser.add_argument('part_number', type=str, help='Part number or order number to import')

args = parser.parse_args()
if args.o:
    if len(sys.argv) > 1:
        ordernum = args.part_number
    else:
        ordernum = input("Enter a Digikey Order Number > ")

    import_digikey_order(ordernum)
elif args.history:
    import_order_history()
elif args.bom:
    import_octopart_bom(args.bom, args.part_number)
else:
    if len(sys.argv) > 1:
        partnum = args.part_number
    else:
        partnum = input("Enter a digikey Part Number > ")

    import_digikey_part(partnum, not args.y)
