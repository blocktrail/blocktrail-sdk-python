from pycoin.key.BIP32Node import BIP32Node
from pycoin.scripts.genwallet import b2h
from pycoin.serialize import b2h_rev, h2b
from pycoin.tx.Spendable import Spendable
from pycoin.tx.pay_to import ScriptMultisig, address_for_pay_to_script, build_hash160_lookup
from pycoin.tx.tx_utils import create_tx

VERIFY_NEW_DERIVATIONS = True

class Wallet(object):


    def __init__(self, client, identifier, primary_mnemonic, primary_private_key, backup_public_key, blocktrail_public_keys, key_index, testnet):
        """
        @type primary_private_key: BIP32Node
        @type backup_public_key: BIP32Node
        """
        self.client = client
        self.identifier = identifier
        self.primary_mnemonic = primary_mnemonic
        self.primary_private_key = primary_private_key
        self.backup_public_key = backup_public_key

        self.blocktrail_public_keys = dict([(str(key_index), BIP32Node.from_hwif(key[0])) for key_index, key in blocktrail_public_keys.items()])
        self.key_index = int(key_index)
        self.testnet = testnet
        self.netcode = "XTN" if self.testnet else "BTC"

    def get_new_address_pair(self):
        path = self.get_new_derivation()
        address = self.get_address_by_path(path)

        return path, address

    def get_new_derivation(self):
        parent_path = "M/%d'/0" % self.key_index
        result = self.client.get_new_derivation(self.identifier, path=parent_path)

        path = result['path']

        if VERIFY_NEW_DERIVATIONS:
            if result['address'] != self.get_address_by_path(path):
                raise Exception("Failed to verify that address from API matches address locally")

        return path

    def get_address_by_path(self, path):
        path = path.replace("M/", "")
        key_index = path.split("/")[0].replace("'", "")

        key = self.primary_private_key.subkey_for_path(path)
        backup_public_key = self.backup_public_key.subkey_for_path(path.replace("'", ""))
        blocktrail_public_key = self.blocktrail_public_keys[str(key_index)].subkey_for_path("/".join(path.split("/")[1:]))

        script = ScriptMultisig(2, sorted([
            key.sec(use_uncompressed=False),
            backup_public_key.sec(use_uncompressed=False),
            blocktrail_public_key.sec(use_uncompressed=False),
        ])).script()

        return address_for_pay_to_script(script, netcode=self.netcode)

    def get_balance(self):
        balance_info = self.client.get_wallet_balance(self.identifier)

        return balance_info['confirmed'], balance_info['unconfirmed']

    def pay(self, pay, change_address=None, allow_zero_conf=False, randomize_change_idx=True):
        send = {}

        if isinstance(pay, list):
            for address, value in pay:
                send[address] = value
        else:
            send = pay

        coin_selection = self.client.coin_selection(self.identifier, send, lockUTXO=True, allow_zero_conf=allow_zero_conf)

        utxos = coin_selection['utxos']
        fee = coin_selection['fee']
        change = coin_selection['change']

        if change > 0:
            if change_address is None:
                _, change_address = self.get_new_address_pair()

            send[change_address] = change

        print(utxos)

        spendables = [Spendable.from_dict(dict(
            coin_value=utxo['value'],
            script_hex=utxo['redeem_script'],
            tx_hash_hex=b2h_rev(h2b(utxo['hash'])),
            tx_out_index=utxo['idx']
        )) for utxo in utxos]

        print(spendables, send)

        tx = create_tx(spendables, send)

        keys = []
        for utxo in utxos:
            path = utxo['path'].replace("M/", "")
            key = self.primary_private_key.subkey_for_path(path)
            keys.append(key)

        hash160_lookup = build_hash160_lookup(key.secret_exponent() for key in keys)
        tx.sign(hash160_lookup=hash160_lookup)

        print(tx, tx.as_hex(include_unspents=True))

        signed = self.client.send_transaction(self.identifier, tx.as_hex(include_unspents=True), [utxo['path'] for utxo in utxos], check_fee=True)

        print(signed)

        return signed['txid']

