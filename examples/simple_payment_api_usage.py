from __future__ import print_function
import blocktrail
from blocktrail.exceptions import ObjectNotFound

client = blocktrail.APIClient("MY_APIKEY", "MY_APISECRET", testnet=True)

try:
    wallet = client.init_wallet("example-wallet", "example-strong-password")
except ObjectNotFound:
    wallet, primary_mnemonic, backup_mnemonic, blocktrail_pubkeys = client.create_new_wallet("example-wallet", "example-strong-password", key_index=9999)
    wallet.do_discovery()

print(wallet.get_new_address_pair())

print(wallet.get_balance())

path, address = wallet.get_new_address_pair()

print(wallet.pay([(address, blocktrail.to_satoshi(0.001))]))