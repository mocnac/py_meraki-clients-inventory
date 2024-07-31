import meraki
import csv
import argparse
import getpass
import logging
import sys
from datetime import datetime
try:
    import pandas
except:
    print("Module 'pandas' not found, therefore exports into .xls are not possible.")
else:
    import pandas
    v_pandas = True

#################################################################################################
# inline arguments - otherwise use arguments "-K / -O"
# API_KEY = ""
# ORG_ID  = 1234
# OUT_FILE = ""
# TIMESPAN = 1d
#################################################################################################
parser = argparse.ArgumentParser()
parser.add_argument('-K', '--api_key', help='Your API Key', default = '', required=False)
parser.add_argument('-O', '--org_id', help='Your Organization ID', default = '', required=False)
parser.add_argument('-F', '--out_file', help='Target file name', default = '', required=False)
parser.add_argument('-S', '--timespan', help='Timespan to search for Clients (in days)', required=False)
parser.add_argument('-T', '--out_type', help='Target file type', default = 'csv', required=False, choices=["xls","csv"])
parser.add_argument('-v', '--verbose', help='Run Script with informational (-v) or debugging (-vv) logging output. For troubleshooting purposes.', action='count', required=False)
parser.add_argument('-f', '--filter-network-tags', help='string to filter for network tags', default = '', required=False)
args = parser.parse_args()

if not args.api_key:
    try: API_KEY
    except: 
        args.api_pwd = getpass.getpass(prompt="Enter API Key:")
        if args.api_pwd == '': 
            print("Key given - aborting!")
            sys.exit(1)
    else: args.api_key = API_KEY
if not args.org_id:
    try: ORG_ID
    except: 
        args.org_id = getpass.getpass(prompt="Enter ORG ID:")
        if args.org_id == '': 
            print("No ID given - aborting!")
            sys.exit(1)
    else: args.org_id = ORG_ID

if not args.out_file:
    try: OUT_FILE
    except: 
        args.out_file = getpass.getpass(prompt="Enter target file name:")
        if args.out_file == '':
            ts=datetime.now().strftime('%Y%m%d-%H%M')
            print("No file name given - using default (meraki_clients-{}.csv/.xlsx)!".format(ts))
            args.out_file = "meraki_clients-{}.csv".format(ts)
    else: args.out_file = OUT_FILE


if not args.timespan:
    try: args.timespan = TIMESPAN
    except: 
        print('no timespan given, defaulting to 1 day (1d)')
        args.timespan = '1d'
match args.timespan[-1:]:
    case 'd':
        args.timespan = int(args.timespan[:-1]) * 86400
    case 'h':
        args.timespan = int(args.timespan[:-1]) * 3600
    case 'm':
        args.timespan = int(args.timespan[:-1]) * 60
    case 's':
        args.timespan = int(args.timespan[:-1])
    case _:
        print("invalid timespan - please retry! (examples: 1d(ay), 2m(inutes), 24h(ours))")
        sys.exit(1)

if args.timespan > 1209600:
    input("################## Maximum timespan is 14 days - due to API limits! ##################\nPress Enter to continue...")
#    args.timespan = 1209600

#################################################################################################
# ADDING DEBUG MODE                                                                             #
#################################################################################################
if args.verbose == 1:
    logging.basicConfig(level=logging.INFO)
    logging.info("################## Starting - With informational Logging ##################")
elif args.verbose == 2:
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("################## Starting - With verbose Logging ##################")
else: print("##################      Starting      ##################")

#################################################################################################
try:
    meraki.DashboardAPI(args.api_key)
except:
    print("API Logon not possible!")
    #print()
    sys.exit(1)
else:
    dashboard = meraki.DashboardAPI(args.api_key)
    if args.verbose == 1: logging.info("Logged On - fetching networks...")
#response = dashboard.organizations.getOrganizations()
try:
    dashboard.organizations.getOrganizationNetworks(args.org_id)
except:
    print("Fetching networks not succeeded!")
    sys.exit(1)
else:
    networks = dashboard.organizations.getOrganizationNetworks(args.org_id)
    if args.verbose == 1: logging.info("Found at least 1 network ... continuing")

lines = []
line = []
for a in networks:
#    print(a['id'])
    if not "systemsManager" in str(a['productTypes']):
        if "vpn_spoke" in a['tags']:
            b=dashboard.networks.getNetworkClients(networkId=a['id'],timespan=float(args.timespan),perPage=1000, total_pages=-1)
            # print(b)
            for clients in b:
                clients['network'] = a['name']
                lines.append(clients)
            else: pass


with open(args.out_file, 'w',newline='') as file:
    writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(clients.keys())
    for line in lines:
        line.update((k, "N/A") for k, v in line.items() if v == None)
        line.update((k, "False") for k, v in line.items() if v == False)
        line.update((k, "True") for k, v in line.items() if v == True)
        writer.writerow(line.values())

if args.out_type == "xls" and v_pandas == True:
    df = pandas.read_csv(args.out_file)
    # Possible columns:
    # id, mac, description, ip, ip6, ip6Local, user, firstSeen, lastSeen, manufacturer, os, deviceTypePrediction, recentDeviceSerial, recentDeviceName, recentDeviceMac, recentDeviceConnection, ssid, vlan, switchport, usage, status, notes, groupPolicy8021x, adaptivePolicyGroup, smInstalled, namedVlan, pskGroup, wirelessCapabilities, network
    df = df[['id','network','mac','ip','ip6','description','firstSeen','lastSeen','manufacturer','os','recentDeviceSerial','recentDeviceName', 'switchport','recentDeviceConnection', 'ssid', 'vlan', 'usage', 'status']]
    with pandas.ExcelWriter(args.out_file.replace("csv","xlsx"), engine = 'xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='mrk clients', index = False)

print("################## DONE - Results have been written to {0} ##################".format(args.out_file))
