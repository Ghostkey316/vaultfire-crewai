"""
VaultfireClient — web3.py wrapper for Vaultfire Protocol smart contracts.

Supports Base (primary hub), Avalanche, Arbitrum, and Polygon.
Write operations require PRIVATE_KEY in the environment.

Usage:
    client = VaultfireClient(chain="base")
    result = client.verify_trust("0xABCD...")
"""

import os
import time
from typing import Any, Dict, List, Optional

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from .abis import IDENTITY_ABI, PARTNERSHIP_ABI, REPUTATION_ABI, BRIDGE_ABI
from .chains import ChainConfig, get_chain, DEFAULT_CHAIN
from .scoring import calculate_street_cred, ScoreBreakdown


class VaultfireClient:
    """
    Client for interacting with Vaultfire Protocol contracts.

    Parameters
    ----------
    chain:
        Chain name — "base" (default), "avalanche", "arbitrum", or "polygon".
    rpc_url:
        Override the default RPC URL for the chain.
    """

    def __init__(self, chain: str = DEFAULT_CHAIN, rpc_url: Optional[str] = None):
        self.chain_config: ChainConfig = get_chain(chain)
        self._rpc_url = rpc_url or self.chain_config.rpc_url

        self.w3 = Web3(Web3.HTTPProvider(self._rpc_url))

        # Inject PoA middleware for Polygon and Avalanche
        if chain in ("polygon", "avalanche"):
            self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        # Lazy-initialised contract handles
        self._identity_contract = None
        self._partnership_contract = None
        self._reputation_contract = None
        self._bridge_contract = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @property
    def contracts(self):
        return self.chain_config.contracts

    def _identity(self):
        if self._identity_contract is None:
            self._identity_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts.identity),
                abi=IDENTITY_ABI,
            )
        return self._identity_contract

    def _partnership(self):
        if self._partnership_contract is None:
            self._partnership_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts.partnership),
                abi=PARTNERSHIP_ABI,
            )
        return self._partnership_contract

    def _reputation(self):
        if self._reputation_contract is None:
            self._reputation_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts.reputation),
                abi=REPUTATION_ABI,
            )
        return self._reputation_contract

    def _bridge(self):
        if self._bridge_contract is None:
            self._bridge_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contracts.bridge),
                abi=BRIDGE_ABI,
            )
        return self._bridge_contract

    def _get_signer(self):
        """Load account from PRIVATE_KEY environment variable."""
        private_key = os.environ.get("PRIVATE_KEY")
        if not private_key:
            raise EnvironmentError(
                "PRIVATE_KEY environment variable is required for write operations."
            )
        account = self.w3.eth.account.from_key(private_key)
        return account

    def _send_tx(self, fn, value: int = 0) -> Dict[str, Any]:
        """Build, sign, and send a transaction; wait for receipt."""
        account = self._get_signer()
        nonce = self.w3.eth.get_transaction_count(account.address)
        gas_price = self.w3.eth.gas_price

        tx = fn.build_transaction(
            {
                "from": account.address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "value": value,
            }
        )
        tx["gas"] = self.w3.eth.estimate_gas(tx)

        signed = self.w3.eth.account.sign_transaction(tx, account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        return {
            "tx_hash": receipt.transactionHash.hex(),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "status": "success" if receipt.status == 1 else "failed",
        }

    # ------------------------------------------------------------------
    # READ — Identity
    # ------------------------------------------------------------------

    def get_agent(self, address: str) -> Dict[str, Any]:
        """Fetch on-chain identity data for an address."""
        checksum = Web3.to_checksum_address(address)
        raw = self._identity().functions.getAgent(checksum).call()
        return {
            "address": checksum,
            "agentURI": raw[0],
            "active": raw[1],
            "agentType": raw[2],
            "registeredAt": raw[3],
        }

    def is_agent_active(self, address: str) -> bool:
        checksum = Web3.to_checksum_address(address)
        return self._identity().functions.isAgentActive(checksum).call()

    def get_total_agents(self) -> int:
        return self._identity().functions.getTotalAgents().call()

    def discover_agents_by_capability(self, capabilities_hash: bytes) -> List[str]:
        """Return list of agent addresses that match a capabilities hash."""
        return self._identity().functions.discoverAgentsByCapability(
            capabilities_hash
        ).call()

    # ------------------------------------------------------------------
    # READ — Partnership
    # ------------------------------------------------------------------

    def get_bond(self, bond_id: int) -> Dict[str, Any]:
        """Fetch a single bond by ID."""
        raw = self._partnership().functions.getBond(bond_id).call()
        return {
            "bondId": raw[0],
            "human": raw[1],
            "aiAgent": raw[2],
            "partnershipType": raw[3],
            "stakeAmount": raw[4],
            "createdAt": raw[5],
            "distributionRequestedAt": raw[6],
            "distributionPending": raw[7],
            "active": raw[8],
        }

    def get_bonds_by_participant(self, address: str) -> List[Dict[str, Any]]:
        """Fetch all bonds for an address and return full bond objects."""
        checksum = Web3.to_checksum_address(address)
        bond_ids: List[int] = self._partnership().functions.getBondsByParticipant(
            checksum
        ).call()
        bonds = []
        for bond_id in bond_ids:
            try:
                bonds.append(self.get_bond(bond_id))
            except Exception:
                pass
        return bonds

    def get_next_bond_id(self) -> int:
        return self._partnership().functions.nextBondId().call()

    def get_total_active_bond_value(self) -> int:
        """Return total active bond value in Wei."""
        return self._partnership().functions.totalActiveBondValue().call()

    # ------------------------------------------------------------------
    # READ — Reputation
    # ------------------------------------------------------------------

    def get_reputation(self, address: str) -> Dict[str, Any]:
        checksum = Web3.to_checksum_address(address)
        raw = self._reputation().functions.getReputation(checksum).call()
        return {
            "address": checksum,
            "averageRating": raw[0],
            "totalFeedbacks": raw[1],
            "verifiedFeedbacks": raw[2],
            "lastUpdated": raw[3],
        }

    # ------------------------------------------------------------------
    # READ — Bridge
    # ------------------------------------------------------------------

    def is_agent_recognized(self, address: str) -> bool:
        checksum = Web3.to_checksum_address(address)
        return self._bridge().functions.isAgentRecognized(checksum).call()

    def get_synced_agent_count(self) -> int:
        return self._bridge().functions.getSyncedAgentCount().call()

    # ------------------------------------------------------------------
    # Composite reads
    # ------------------------------------------------------------------

    def get_street_cred(self, address: str) -> Dict[str, Any]:
        """
        Compute Street Cred score for an address.

        Returns dict with 'score' (ScoreBreakdown.to_dict()) and raw inputs.
        """
        agent_data = self.get_agent(address)
        is_registered = bool(agent_data.get("active", False)) or bool(
            agent_data.get("agentURI", "")
        )
        bonds = self.get_bonds_by_participant(address)
        score: ScoreBreakdown = calculate_street_cred(is_registered, bonds)
        return {
            "address": Web3.to_checksum_address(address),
            "chain": self.chain_config.name,
            "score": score.to_dict(),
            "agent": agent_data,
            "bond_count": len(bonds),
        }

    def verify_trust(self, address: str, min_score: int = 20) -> Dict[str, Any]:
        """
        Full trust verification for an agent address.

        Checks identity, bonds, Street Cred score, reputation, and bridge sync.
        Returns a structured verdict dict.
        """
        checksum = Web3.to_checksum_address(address)

        # Collect all data (best-effort — individual calls may fail on unregistered agents)
        agent_data: Dict[str, Any] = {}
        bonds: List[Dict[str, Any]] = []
        reputation: Dict[str, Any] = {}
        bridge_recognized = False

        try:
            agent_data = self.get_agent(checksum)
        except Exception as e:
            agent_data = {"error": str(e)}

        try:
            bonds = self.get_bonds_by_participant(checksum)
        except Exception as e:
            bonds = []

        try:
            reputation = self.get_reputation(checksum)
        except Exception as e:
            reputation = {"error": str(e)}

        try:
            bridge_recognized = self.is_agent_recognized(checksum)
        except Exception:
            pass

        is_registered = (
            agent_data.get("active", False)
            or bool(agent_data.get("agentURI", ""))
        )
        score: ScoreBreakdown = calculate_street_cred(is_registered, bonds)

        trusted = score.total >= min_score
        verdict = "TRUSTED" if trusted else "UNTRUSTED"

        return {
            "address": checksum,
            "chain": self.chain_config.name,
            "chain_id": self.chain_config.chain_id,
            "verdict": verdict,
            "trusted": trusted,
            "min_score_required": min_score,
            "street_cred": score.to_dict(),
            "identity": agent_data,
            "bonds": bonds,
            "reputation": reputation,
            "bridge_recognized": bridge_recognized,
            "timestamp": int(time.time()),
        }

    def get_protocol_stats(self) -> Dict[str, Any]:
        """Aggregate protocol-wide statistics from all contracts."""
        stats: Dict[str, Any] = {
            "chain": self.chain_config.name,
            "chain_id": self.chain_config.chain_id,
        }

        try:
            stats["total_agents"] = self.get_total_agents()
        except Exception as e:
            stats["total_agents_error"] = str(e)

        try:
            stats["next_bond_id"] = self.get_next_bond_id()
            stats["total_bonds"] = max(0, stats["next_bond_id"] - 1)
        except Exception as e:
            stats["bonds_error"] = str(e)

        try:
            total_value_wei = self.get_total_active_bond_value()
            stats["total_active_bond_value_wei"] = total_value_wei
            stats["total_active_bond_value_eth"] = float(
                Web3.from_wei(total_value_wei, "ether")
            )
        except Exception as e:
            stats["bond_value_error"] = str(e)

        try:
            stats["synced_agent_count"] = self.get_synced_agent_count()
        except Exception as e:
            stats["synced_agent_count_error"] = str(e)

        stats["timestamp"] = int(time.time())
        return stats

    # ------------------------------------------------------------------
    # WRITE — Identity
    # ------------------------------------------------------------------

    def register_agent(
        self,
        agent_uri: str,
        agent_type: str,
        capabilities_hash: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Register an AI agent on-chain.

        Requires PRIVATE_KEY environment variable.

        Parameters
        ----------
        agent_uri:
            URI pointing to agent metadata (e.g. IPFS CID or HTTPS URL).
        agent_type:
            Free-form string describing the agent type.
        capabilities_hash:
            32-byte capabilities hash. Defaults to zero bytes if not provided.
        """
        if capabilities_hash is None:
            capabilities_hash = b"\x00" * 32
        if len(capabilities_hash) != 32:
            raise ValueError("capabilities_hash must be exactly 32 bytes")

        fn = self._identity().functions.registerAgent(
            agent_uri, agent_type, capabilities_hash
        )
        receipt = self._send_tx(fn)
        receipt["agent_uri"] = agent_uri
        receipt["agent_type"] = agent_type
        receipt["chain"] = self.chain_config.name
        return receipt

    # ------------------------------------------------------------------
    # WRITE — Partnership
    # ------------------------------------------------------------------

    def create_bond(
        self,
        ai_agent_address: str,
        partnership_type: str,
        stake_eth: float,
    ) -> Dict[str, Any]:
        """
        Create a partnership bond with an AI agent.

        Requires PRIVATE_KEY environment variable.

        Parameters
        ----------
        ai_agent_address:
            Address of the AI agent to bond with.
        partnership_type:
            String describing the partnership type.
        stake_eth:
            Amount of ETH (or native token) to stake in the bond.
        """
        ai_agent_checksum = Web3.to_checksum_address(ai_agent_address)
        stake_wei = Web3.to_wei(stake_eth, "ether")

        fn = self._partnership().functions.createBond(
            ai_agent_checksum, partnership_type
        )
        receipt = self._send_tx(fn, value=stake_wei)
        receipt["ai_agent"] = ai_agent_checksum
        receipt["partnership_type"] = partnership_type
        receipt["stake_eth"] = stake_eth
        receipt["chain"] = self.chain_config.name
        return receipt
