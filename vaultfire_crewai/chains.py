"""
Chain configurations and contract addresses for Vaultfire Protocol.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ContractAddresses:
    identity: str
    partnership: str
    accountability: str
    reputation: str
    bridge: str


@dataclass
class ChainConfig:
    chain_id: int
    name: str
    rpc_url: str
    contracts: ContractAddresses
    native_currency: str = "ETH"


# ------------------------------------------------------------------
# Contract addresses per chain
# ------------------------------------------------------------------

BASE_CONTRACTS = ContractAddresses(
    identity="0x35978DB675576598F0781dA2133E94cdCf4858bC",
    partnership="0xC574CF2a09B0B470933f0c6a3ef422e3fb25b4b4",
    accountability="0xf92baef9523BC264144F80F9c31D5c5C017c6Da8",
    reputation="0xdB54B8925664816187646174bdBb6Ac658A55a5F",
    bridge="0x94F54c849692Cc64C35468D0A87D2Ab9D7Cb6Fb2",
)

AVALANCHE_CONTRACTS = ContractAddresses(
    identity="0x57741F4116925341d8f7Eb3F381d98e07C73B4a3",
    partnership="0xea6B504827a746d781f867441364C7A732AA4b07",
    accountability="0xaeFEa985E0C52f92F73606657B9dA60db2798af3",
    reputation="0x11C267C8A75B13A4D95357CEF6027c42F8e7bA24",
    bridge="0x0dF0523aF5aF2Aef180dB052b669Bea97fee3d31",
)

# Arbitrum and Polygon share the same addresses
ARBITRUM_POLYGON_CONTRACTS = ContractAddresses(
    identity="0x6298c62FDA57276DC60de9E716fbBAc23d06D5F1",
    partnership="0x0E777878C5b5248E1b52b09Ab5cdEb2eD6e7Da58",
    accountability="0xfDdd2B1597c87577543176AB7f49D587876563D2",
    reputation="0x8aceF0Bc7e07B2dE35E9069663953f41B5422218",
    bridge="0xe2aDfe84703dd6B5e421c306861Af18F962fDA91",
)

# ------------------------------------------------------------------
# Chain configs
# ------------------------------------------------------------------

CHAINS: Dict[str, ChainConfig] = {
    "base": ChainConfig(
        chain_id=8453,
        name="Base",
        rpc_url="https://mainnet.base.org",
        contracts=BASE_CONTRACTS,
        native_currency="ETH",
    ),
    "avalanche": ChainConfig(
        chain_id=43114,
        name="Avalanche",
        rpc_url="https://api.avax.network/ext/bc/C/rpc",
        contracts=AVALANCHE_CONTRACTS,
        native_currency="AVAX",
    ),
    "arbitrum": ChainConfig(
        chain_id=42161,
        name="Arbitrum One",
        rpc_url="https://arbitrum-one.publicnode.com",
        contracts=ARBITRUM_POLYGON_CONTRACTS,
        native_currency="ETH",
    ),
    "polygon": ChainConfig(
        chain_id=137,
        name="Polygon",
        rpc_url="https://polygon-bor-rpc.publicnode.com",
        contracts=ARBITRUM_POLYGON_CONTRACTS,
        native_currency="MATIC",
    ),
}

SUPPORTED_CHAINS = list(CHAINS.keys())
DEFAULT_CHAIN = "base"


def get_chain(chain: str) -> ChainConfig:
    """Return chain configuration by name (case-insensitive)."""
    key = chain.lower()
    if key not in CHAINS:
        raise ValueError(
            f"Unsupported chain '{chain}'. Supported: {SUPPORTED_CHAINS}"
        )
    return CHAINS[key]
