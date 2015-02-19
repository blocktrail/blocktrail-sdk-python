from bitcoin.deterministic import bip32_ckd, bip32_extract_key, bip32_privtopub
from bitcoin.transaction import mk_multisig_script, p2sh_scriptaddr, mktx, multisign, serialize, deserialize, \
    apply_multisignatures

VERIFY_NEW_DERIVATIONS = True


def bip32_build_key(data, path):
    path = path.replace("M/", "")
    path = path.split("/")

    for p in path:
        p = int(p.replace("'", "")) + 2**31 if "'" in p else int(p)
        data = bip32_ckd(data, p)

    return data


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

        self.blocktrail_public_keys = dict([(str(key_index), key[0]) for key_index, key in blocktrail_public_keys.items()])
        self.key_index = int(key_index)
        self.testnet = testnet
        self.p2sh_magicbyte = 0xc4 if self.testnet else 0x05

    def get_new_address_pair(self):
        path = self.get_new_derivation()
        address = self.get_address_by_path(path)

        return path, address

    def get_new_derivation(self):
        parent_path = "M/%d'/0" % self.key_index
        result = self.client.get_new_derivation(self.identifier, path=parent_path)

        path = result['path']

        if VERIFY_NEW_DERIVATIONS:
            address = self.get_address_by_path(path)
            if result['address'] != address:
                raise Exception("Failed to verify that address from API [%s] matches address locally [%s]" % (result['address'], address))

        return path

    def get_address_by_path(self, path):
        key_index = path.split("/")[1].replace("'", "")

        primary_public_key = bip32_privtopub(bip32_build_key(self.primary_private_key, path))

        backup_public_key = bip32_build_key(self.backup_public_key, path.replace("'", ""))
        blocktrail_public_key = bip32_build_key(self.blocktrail_public_keys[str(key_index)], "/".join(path.split("/")[2:]))

        script = mk_multisig_script(sorted([
            bip32_extract_key(primary_public_key),
            bip32_extract_key(backup_public_key),
            bip32_extract_key(blocktrail_public_key),
        ]), 2, 3)

        return p2sh_scriptaddr(script, magicbyte=self.p2sh_magicbyte)

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

        spendables = [dict(
            value=utxo['value'],
            address=utxo['address'],
            output="%s:%s" % (utxo['hash'], utxo['idx'])
        ) for utxo in utxos]

        tx = mktx(spendables, [{'address': address, 'value': value} for address, value in send.items()])

        i = 0
        for utxo in utxos:
            key = bip32_build_key(self.primary_private_key, utxo['path'])
            tx = apply_multisignatures(tx, i, utxo['redeem_script'], [multisign(tx, i, utxo['redeem_script'], bip32_extract_key(key))])
            i += 1

        signed = self.client.send_transaction(self.identifier, tx, [utxo['path'] for utxo in utxos], check_fee=True)

        return signed['txid']

