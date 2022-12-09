import binascii
import time

from stellar_sdk import Network, Keypair, TransactionBuilder
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban import SorobanServer
from stellar_sdk.soroban.soroban_rpc import TransactionStatus
from stellar_sdk.soroban_types import AccountId, Int128, Bytes, Uint64

parent_secret = "SAAPYAPTTRZMCUZFPG3G66V4ZMHTK4TWA6NS7U4F7Z3IMUD52EK4DDEV"
child_secret = "SAPSRJQIL4WLQZMB6IYXA6FLY5TS2WX7PDFLWN3RP7AD6GS3DRHHCN54"
native_asset_contract_id = (
    "71c670db8b9d9dd3fa17d83bd98e4a9814f926121972774bd419fa402fe01dc7"
)
asset_interop_contract_id = (
    "753943e1ffce317449f9fe12769ac9a6c3aa657cb2b2261f7a677e460a08816d"
)

rpc_server_url = "https://horizon-futurenet.stellar.cash/soroban/rpc"
network_passphrase = Network.FUTURENET_NETWORK_PASSPHRASE

parent_kp = Keypair.from_secret(parent_secret)
child_kp = Keypair.from_secret(child_secret)
soroban_server = SorobanServer(rpc_server_url)
source = soroban_server.load_account(parent_kp.public_key)

tx = (
    TransactionBuilder(source, network_passphrase)
    .set_timeout(300)
    .append_invoke_contract_function_op(
        contract_id=asset_interop_contract_id,
        method="init",
        parameters=[
            AccountId(child_kp.public_key),
            Bytes(binascii.unhexlify(native_asset_contract_id)),
            Int128(500 * 10**7),
            Uint64(1 * 10**1),
        ],
    )
    .build()
)

simulate_transaction_data = soroban_server.simulate_transaction(tx)
print(f"simulated transaction: {simulate_transaction_data}")
assert simulate_transaction_data.results

# The footpoint is predictable, maybe we can optimize the code to omit this step
print(f"setting footprint and signing transaction...")
tx.set_footpoint(simulate_transaction_data.footprint)
tx.sign(parent_kp)

send_transaction_data = soroban_server.send_transaction(tx)
print(f"sent transaction: {send_transaction_data}")

while True:
    print("waiting for transaction to be confirmed...")
    get_transaction_status_data = soroban_server.get_transaction_status(
        send_transaction_data.id
    )
    if get_transaction_status_data.status != TransactionStatus.PENDING:
        break
    time.sleep(3)
print(f"transaction status: {get_transaction_status_data}")

if get_transaction_status_data.status == TransactionStatus.SUCCESS:
    result = stellar_xdr.SCVal.from_xdr(get_transaction_status_data.results[0].xdr)  # type: ignore
    print(result)
