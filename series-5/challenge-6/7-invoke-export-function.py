import time

from stellar_sdk import Network, Keypair, TransactionBuilder
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban import SorobanServer
from stellar_sdk.soroban.soroban_rpc import TransactionStatus
from stellar_sdk.soroban_types import InvokerSignature, Int128, Int64

child_secret = "SAPSRJQIL4WLQZMB6IYXA6FLY5TS2WX7PDFLWN3RP7AD6GS3DRHHCN54"
native_asset_contract_id = (
    "71c670db8b9d9dd3fa17d83bd98e4a9814f926121972774bd419fa402fe01dc7"
)

rpc_server_url = "https://horizon-futurenet.stellar.cash/soroban/rpc"
network_passphrase = Network.FUTURENET_NETWORK_PASSPHRASE

child_kp = Keypair.from_secret(child_secret)
soroban_server = SorobanServer(rpc_server_url)
source = soroban_server.load_account(child_kp.public_key)

tx = (
    TransactionBuilder(source, network_passphrase)
    .set_timeout(300)
    .append_invoke_contract_function_op(
        contract_id=native_asset_contract_id,
        method="export",
        parameters=[
            InvokerSignature(),  # Invoker
            Int128(0),  # Nonce
            Int64(1 * 10**7),  # amount, 1 tokens
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
tx.sign(child_kp)

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
