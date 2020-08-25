import requests
import json

url = "https://api.upfrontdelivery.co.ke/m-pesa/c2b/confirmation"

# ALWAYS CHANGE THE TransID , BillRefNumber, MSISDN
payload = {
    "TransactionType": "Pay Bill",
    "TransID": "OHMA4565LW1",
    "TransTime": "20200821163231",
    "TransAmount": "750.00",
    "BusinessShortCode": "932280",
    "BillRefNumber": "steveTest12",
    "InvoiceNumber": "",
    "OrgAccountBalance": "755.00",
    "ThirdPartyTransID": "",
    "MSISDN": "254745021668",
    "FirstName": "STEVEN",
    "MiddleName": "ONDIEKI",
    "LastName": "OMWANGE"
}


headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data = json.dumps(payload))

print(response.text.encode('utf8'))
