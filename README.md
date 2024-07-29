# py_meraki-clients-inventory
fetching clients from meraki networks - orgwide

## Help:
```
usage: meraki_inventory.py [-h] [-K API_KEY] [-O ORG_ID] [-F OUT_FILE] [-T {xls,csv}] [-v] [-f FILTER_NETWORK_TAGS]

options:
  -h, --help            show this help message and exit
  -K API_KEY, --api_key API_KEY
                        Your API Key
  -O ORG_ID, --org_id ORG_ID
                        Your Organization ID
  -F OUT_FILE, --out_file OUT_FILE
                        Target file name
  -T {xls,csv}, --out_type {xls,csv}
                        Target file type
  -v, --verbose         Run Script with informational (-v) or debugging (-vv) logging output. For troubleshooting purposes.
  -f FILTER_NETWORK_TAGS, --filter-network-tags FILTER_NETWORK_TAGS
                        string to filter for network tags
```

