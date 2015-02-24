import struct
import random
from pycoin.key.BIP32Node import BIP32Node
from bitcoin.core import x, b2x, lx, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction
from bitcoin.core.script import CScript, SignatureHash, SIGHASH_ALL, OP_CHECKMULTISIG, OP_0
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret, P2PKHBitcoinAddress

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

        self.blocktrail_public_keys = dict([(str(_key_index), BIP32Node.from_hwif(_key[0])) for _key_index, _key in blocktrail_public_keys.items()])
        self.key_index = int(key_index)
        self.testnet = testnet

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

    def get_address_by_path(self, path, key=None):
        path = path.replace("M/", "")
        key_index = path.split("/")[0].replace("'", "")

        if key is None:
            key = self.primary_private_key.subkey_for_path(path)

        backup_public_key = self.backup_public_key.subkey_for_path(path.replace("'", ""))
        blocktrail_public_key = self.blocktrail_public_keys[str(key_index)].subkey_for_path("/".join(path.split("/")[1:]))

        redeemScript = CScript([2] + sorted([
            key.sec(use_uncompressed=False),
            backup_public_key.sec(use_uncompressed=False),
            blocktrail_public_key.sec(use_uncompressed=False),
        ]) + [3, OP_CHECKMULTISIG])

        scriptPubKey = redeemScript.to_p2sh_scriptPubKey()
        address = CBitcoinAddress.from_scriptPubKey(scriptPubKey)

        return str(address)

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

        txins = []
        for utxo in utxos:
            txins.append(CMutableTxIn(COutPoint(lx(utxo['hash']), utxo['idx'])))

        txouts = []
        change_txout = None
        for address, value in send.items():
            txout = CMutableTxOut(value, CBitcoinAddress(address).to_scriptPubKey())
            if address == change_address:
                change_txout = txout
            txouts.append(txout)

        # randomly move the change_txout
        if randomize_change_idx and change_txout:
            txouts.remove(change_txout)
            txouts.insert(random.randrange(len(txouts) + 1), change_txout)

        tx = CMutableTransaction(txins, txouts)

        for idx, utxo in enumerate(utxos):
            path = utxo['path'].replace("M/", "")

            key = self.primary_private_key.subkey_for_path(path)
            redeemScript = CScript(x(utxo['redeem_script']))
            sighash = SignatureHash(redeemScript, tx, idx, SIGHASH_ALL)

            ckey = CBitcoinSecret(key.wif())

            sig = ckey.sign(sighash) + struct.pack("B", SIGHASH_ALL)

            txins[idx].scriptSig = CScript([OP_0, sig, redeemScript])

        signed = self.client.send_transaction(self.identifier, b2x(tx.serialize()), [utxo['path'] for utxo in utxos], check_fee=True)

        return signed['txid']

    def do_discovery(self, gap=200):
        balance_info = self.client.wallet_discovery(self.identifier, gap=gap)

        return balance_info['confirmed'], balance_info['unconfirmed']

    def upgrade_key_index(self, key_index):
        primary_public_key = self.primary_private_key.subkey_for_path("%d'.pub" % key_index)

        data = self.client.upgrade_key_index(self.identifier, key_index, (primary_public_key.hwif(), "M/%d'" % key_index))

        self.key_index = key_index
        for blocktrail_key_index, blocktrail_public_key in data['blocktrail_public_keys'].items():
            self.blocktrail_public_keys[str(blocktrail_key_index)] = BIP32Node.from_hwif(blocktrail_public_key[0])

    def delete_wallet(self):
        # can't right now because we can't create a signature
        raise Exception("Not implemented")

        address, signature = self.create_checksum_signature()
        result = self.client.delete_wallet(self.identifier, address, signature)

        return result and result['deleted']

    def create_checksum_signature(self):
        key = CBitcoinSecret(self.primary_private_key.wif())
        address = P2PKHBitcoinAddress.from_pubkey(key.pub)

        signature = None

        print(self.primary_private_key.wif(), str(address))

        return str(address), signature

    def transactions(self, page=1, limit=20):
        return self.client.wallet_transactions(self.identifier, page=page, limit=limit)

    def addresses(self, page=1, limit=20):
        return self.client.wallet_addresses(self.identifier, page=page, limit=limit)

    def setup_webhook(self, url, identifier=None):
        if identifier is None:
            identifier = "WALLET-%s" % (self.identifier, )

        return self.client.setup_wallet_webhook(self.identifier, identifier, url)

    def delete_webhook(self, identifier=None):
        if identifier is None:
            identifier = "WALLET-%s" % (self.identifier, )

        return self.client.delete_wallet_webhook(self.identifier, identifier)
