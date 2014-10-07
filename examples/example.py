import blocktrail

client = blocktrail.APIClient("MYKEY", "MYSECRET")

address = client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")
print address['address'], address['balance']

print client.verify_address("16dwJmR4mX5RguGrocMfN9Q9FR2kZcLw2z", "HPMOHRgPSMKdXrU6AqQs/i9S7alOakkHsJiqLGmInt05Cxj6b/WhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk=")