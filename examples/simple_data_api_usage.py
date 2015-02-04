from __future__ import print_function
import blocktrail

client = blocktrail.APIClient("MY_APIKEY", "MY_APISECRET")

address = client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")
print(address['address'], address['balance'])

print(len(client.address_transactions("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")['data']))

print(client.verify_address("16dwJmR4mX5RguGrocMfN9Q9FR2kZcLw2z", "HPMOHRgPSMKdXrU6AqQs/i9S7alOakkHsJiqLGmInt05Cxj6b/WhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk="))

# Dealing with numbers
print("123456789 Satoshi to BTC: ", blocktrail.to_btc(123456789))
print("1.23456789 BTC to Satoshi: ", blocktrail.to_satoshi(1.23456789))