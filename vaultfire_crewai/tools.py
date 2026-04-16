"""
CrewAI tools for Vaultfire Protocol trust verification.

All tools follow the CrewAI @tool decorator pattern and return JSON strings
so they can be consumed directly by language model agents.

Read tools (no key required):
    vaultfire_verify_agent       — Full trust verification
    vaultfire_get_street_cred    — Street Cred score and tier
    vaultfire_get_agent          — On-chain identity data
    vaultfire_get_bonds          — Partnership bonds for an address
    vaultfire_get_reputation     — Reputation data
    vaultfire_discover_agents    — Find agents by capability hash
    vaultfire_protocol_stats     — Protocol-wide statistics

Write tools (PRIVATE_KEY env var required):
    vaultfire_register_agent     — Register agent on-chain
    vaultfire_create_bond        — Create partnership bond
"""

import json
from typing import Optional

from crewai.tools import tool

from .client import VaultfireClient
from .chains import SUPPORTED_CHAINS, DEFAULT_CHAIN


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _ok(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


def _err(message: str, **kwargs) -> str:
    return json.dumps({"error": message, **kwargs}, indent=2)


# ------------------------------------------------------------------
# READ TOOLS
# ------------------------------------------------------------------

@tool("vaultfire_verify_agent")
def vaultfire_verify_agent(
    address: str,
    chain: str = DEFAULT_CHAIN,
    min_score: int = 20,
) -> str:
    """Verify if an AI agent is trustworthy by checking its on-chain identity,
    partnership bonds, Street Cred score, and reputation on Vaultfire Protocol.
    Returns a trust verdict (TRUSTED / UNTRUSTED) with a full breakdown.

    Args:
        address: Ethereum address of the AI agent to verify (0x...).
        chain: Chain to query — base (default), avalanche, arbitrum, or polygon.
        min_score: Minimum Street Cred score to consider the agent trusted (default 20).

    Returns:
        JSON string with verdict, street_cred score, identity, bonds, and reputation.
    """
    if chain not in SUPPORTED_CHAINS:
        return _err(f"Unsupported chain '{chain}'", supported=SUPPORTED_CHAINS)
    try:
        client = VaultfireClient(chain=chain)
        result = client.verify_trust(address, min_score=min_score)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc), address=address, chain=chain)


@tool("vaultfire_get_street_cred")
def vaultfire_get_street_cred(
    address: str,
    chain: str = DEFAULT_CHAIN,
) -> str:
    """Get the Street Cred score (0-95) and tier for an AI agent address on Vaultfire Protocol.
    Street Cred is a composite on-chain trust score based on identity registration,
    partnership bonds, stake amounts, and multi-bond diversification.
    Tiers: Unranked (0-19), Bronze (20-39), Silver (40-59), Gold (60-79), Platinum (80-95).

    Args:
        address: Ethereum address of the AI agent (0x...).
        chain: Chain to query — base (default), avalanche, arbitrum, or polygon.

    Returns:
        JSON string with score, tier, and detailed point breakdown.
    """
    if chain not in SUPPORTED_CHAINS:
        return _err(f"Unsupported chain '{chain}'", supported=SUPPORTED_CHAINS)
    try:
        client = VaultfireClient(chain=chain)
        result = client.get_street_cred(address)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc), address=address, chain=chain)


@tool("vaultfire_get_agent")
def vaultfire_get_agent(
    address: str,
    chain: str = DEFAULT_CHAIN,
) -> str:
    """Fetch on-chain identity data for an AI agent from the Vaultfire Identity Registry.
    Returns the agent URI, active status, agent type, and registration timestamp.

    Args:
        address: Ethereum address of the AI agent (0x...).
        chain: Chain to query — base (default), avalanche, arbitrum, or polygon.

    Returns:
        JSON string with agentURI, active, agentType, registeredAt fields.
    """
    if chain not in SUPPORTED_CHAINS:
        return _err(f"Unsupported chain '{chain}'", supported=SUPPORTED_CHAINS)
    try:
        client = VaultfireClient(chain=chain)
        result = client.get_agent(address)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc), address=address, chain=chain)


@tool("vaultfire_get_bonds")
def vaultfire_get_bonds(
    address: str,
    chain: str = DEFAULT_CHAIN,
) -> str:
    """Get all partnership bonds for an address from the Vaultfire Partnership contract.
    Returns full bond details including stake amounts, partners, types, and active status.
    Bonds represent committed human-AI partnerships backed by on-chain stake.

    Args:
        address: Ethereum address to look up bonds for (0x...).
        chain: Chain to query — base (default), avalanche, arbitrum, or polygon.

    Returns:
        JSON string with list of bond objects and summary statistics.
    """
    if chain not in SUPPORTED_CHAINS:
        return _err(f"Unsupported chain '{chain}'", supported=SUPPORTED_CHAINS)
    try:
        client = VaultfireClient(chain=chain)
        bonds = client.get_bonds_by_participant(address)
        active_bonds = [b for b in bonds if b.get("active", False)]
        return _ok({
            "address": address,
            "chain": client.chain_config.name,
            "total_bonds": len(bonds),
            "active_bonds": len(active_bonds),
            "bonds": bonds,
        })
    except Exception as exc:
        return _err(str(exc), address=address, chain=chain)


@tool("vaultfire_get_reputation")
def vaultfire_get_reputation(
    address: str,
    chain: str = DEFAULT_CHAIN,
) -> str:
    """Fetch reputation data for an AI agent from the Vaultfire Reputation contract.
    Returns average rating, total feedbacks, verified feedbacks, and last update time.

    Args:
        address: Ethereum address of the AI agent (0x...).
        chain: Chain to query — base (default), avalanche, arbitrum, or polygon.

    Returns:
        JSON string with reputation metrics.
    """
    if chain not in SUPPORTED_CHAINS:
        return _err(f"Unsupported chain '{chain}'", supported=SUPPORTED_CHAINS)
    try:
        client = VaultfireClient(chain=chain)
        result = client.get_reputation(address)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc), address=address, chain=chain)


@tool("vaultfire_discover_agents")
def vaultfire_discover_agents(
    capability: str,
    chain: str = DEFAULT_CHAIN,
) -> str:
    """Discover AI agents on Vaultfire Protocol that match a given capability.
    Accepts a capability name (converted to keccak256 hash) or a raw 0x-prefixed hex hash.
    Returns a list of agent addresses registered with that capability.

    Args:
        capability: Capability name string (e.g. "image-generation") or 0x hex bytes32 hash.
        chain: Chain to query — base (default), avalanche, arbitrum, or polygon.

    Returns:
        JSON string with list of matching agent addresses and count.
    """
    if chain not in SUPPORTED_CHAINS:
        return _err(f"Unsupported chain '{chain}'", supported=SUPPORTED_CHAINS)
    try:
        from web3 import Web3

        # Accept raw hex or compute keccak256 of the string
        if capability.startswith("0x") and len(capability) == 66:
            cap_bytes = bytes.fromhex(capability[2:])
        else:
            cap_bytes = Web3.keccak(text=capability)

        client = VaultfireClient(chain=chain)
        agents = client.discover_agents_by_capability(cap_bytes)
        return _ok({
            "capability": capability,
            "capability_hash": "0x" + cap_bytes.hex(),
            "chain": client.chain_config.name,
            "count": len(agents),
            "agents": agents,
        })
    except Exception as exc:
        return _err(str(exc), capability=capability, chain=chain)


@tool("vaultfire_protocol_stats")
def vaultfire_protocol_stats(chain: str = DEFAULT_CHAIN) -> str:
    """Fetch protocol-wide statistics from Vaultfire Protocol contracts on a given chain.
    Returns total registered agents, bond counts, total staked value, and bridge sync stats.

    Args:
        chain: Chain to query — base (default), avalanche, arbitrum, or polygon.

    Returns:
        JSON string with aggregated protocol statistics.
    """
    if chain not in SUPPORTED_CHAINS:
        return _err(f"Unsupported chain '{chain}'", supported=SUPPORTED_CHAINS)
    try:
        client = VaultfireClient(chain=chain)
        result = client.get_protocol_stats()
        return _ok(result)
    except Exception as exc:
        return _err(str(exc), chain=chain)


# ------------------------------------------------------------------
# WRITE TOOLS
# ------------------------------------------------------------------

@tool("vaultfire_register_agent")
def vaultfire_register_agent(
    agent_uri: str,
    agent_type: str,
    capabilities: str = "",
    chain: str = DEFAULT_CHAIN,
) -> str:
    """Register an AI agent on the Vaultfire Identity Registry.
    This is a WRITE operation that requires the PRIVATE_KEY environment variable.
    The agent URI should point to metadata describing the agent (IPFS CID or HTTPS URL).
    The capabilities string is hashed to bytes32 on-chain.

    Args:
        agent_uri: URI for agent metadata (e.g. "ipfs://Qm..." or "https://...").
        agent_type: Agent type string (e.g. "researcher", "coder", "analyst").
        capabilities: Comma-separated capability list hashed to bytes32 (e.g. "nlp,search,code").
        chain: Chain to register on — base (default), avalanche, arbitrum, or polygon.

    Returns:
        JSON string with transaction hash, block number, gas used, and status.
    """
    if chain not in SUPPORTED_CHAINS:
        return _err(f"Unsupported chain '{chain}'", supported=SUPPORTED_CHAINS)
    try:
        from web3 import Web3

        capabilities_hash = Web3.keccak(text=capabilities) if capabilities else b"\x00" * 32
        client = VaultfireClient(chain=chain)
        result = client.register_agent(agent_uri, agent_type, capabilities_hash)
        return _ok(result)
    except EnvironmentError as exc:
        return _err(
            str(exc),
            hint="Set the PRIVATE_KEY environment variable to your wallet private key.",
        )
    except Exception as exc:
        return _err(str(exc), agent_uri=agent_uri, chain=chain)


@tool("vaultfire_create_bond")
def vaultfire_create_bond(
    ai_agent_address: str,
    partnership_type: str,
    stake_eth: float,
    chain: str = DEFAULT_CHAIN,
) -> str:
    """Create a partnership bond with an AI agent on Vaultfire Protocol.
    This is a WRITE operation that requires the PRIVATE_KEY environment variable.
    Bonds represent committed human-AI partnerships backed by on-chain ETH stake.
    Higher stakes unlock higher bond tiers (Bronze ≥0.01, Silver ≥0.05, Gold ≥0.1, Platinum ≥0.5 ETH).

    Args:
        ai_agent_address: Address of the AI agent to bond with (0x...).
        partnership_type: Type of partnership (e.g. "research", "trading", "creative").
        stake_eth: Amount of ETH to stake in the bond (e.g. 0.1 for 0.1 ETH).
        chain: Chain to create bond on — base (default), avalanche, arbitrum, or polygon.

    Returns:
        JSON string with transaction hash, bond details, and status.
    """
    if chain not in SUPPORTED_CHAINS:
        return _err(f"Unsupported chain '{chain}'", supported=SUPPORTED_CHAINS)
    if stake_eth <= 0:
        return _err("stake_eth must be greater than 0")
    try:
        client = VaultfireClient(chain=chain)
        result = client.create_bond(ai_agent_address, partnership_type, stake_eth)
        return _ok(result)
    except EnvironmentError as exc:
        return _err(
            str(exc),
            hint="Set the PRIVATE_KEY environment variable to your wallet private key.",
        )
    except Exception as exc:
        return _err(str(exc), ai_agent_address=ai_agent_address, chain=chain)


# ------------------------------------------------------------------
# All tools for easy import
# ------------------------------------------------------------------

ALL_TOOLS = [
    vaultfire_verify_agent,
    vaultfire_get_street_cred,
    vaultfire_get_agent,
    vaultfire_get_bonds,
    vaultfire_get_reputation,
    vaultfire_discover_agents,
    vaultfire_protocol_stats,
    vaultfire_register_agent,
    vaultfire_create_bond,
]
