import hashlib

from stellar_sdk import Asset, Network
from stellar_sdk import xdr as stellar_xdr


def get_asset_contract_id(asset: Asset, network_passphrase: str) -> str:
    """Get the contract id of the wrapped token contract."""
    network_id_hash = stellar_xdr.Hash(Network(network_passphrase).network_id())
    data = stellar_xdr.HashIDPreimage(
        stellar_xdr.EnvelopeType.ENVELOPE_TYPE_CONTRACT_ID_FROM_ASSET,
        from_asset=stellar_xdr.HashIDPreimageFromAsset(
            network_id=network_id_hash, asset=asset.to_xdr_object()
        ),
    )
    contract_id = hashlib.sha256(data.to_xdr_bytes()).hexdigest()
    return contract_id


if __name__ == "__main__":
    network_passphrase = "Test SDF Future Network ; October 2022"
    asset = Asset.native()
    print(
        f"Contract ID: {get_asset_contract_id(asset, network_passphrase)}"
    )  # d93f5c7bb0ebc4a9c8f727c5cebc4e41194d38257e1d0d910356b43bfc528813
