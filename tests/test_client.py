"""
Unit tests for vaultfire_crewai.

Tests cover:
- Chain configuration loading
- VaultfireClient initialization
- Street Cred scoring logic
- Score tier mapping
- Bond tier points
- Protocol stat aggregation (mocked)
- verify_trust result structure (mocked web3 calls)
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from web3 import Web3

# ---------------------------------------------------------------------------
# Scoring tests (no network required)
# ---------------------------------------------------------------------------

from vaultfire_crewai.scoring import (
    calculate_street_cred,
    score_to_tier,
    bond_tier_points,
    ScoreBreakdown,
    PLATINUM_THRESHOLD,
    GOLD_THRESHOLD,
    SILVER_THRESHOLD,
    BRONZE_THRESHOLD,
)


class TestScoreToTier(unittest.TestCase):

    def test_unranked(self):
        self.assertEqual(score_to_tier(0), "Unranked")
        self.assertEqual(score_to_tier(19), "Unranked")

    def test_bronze(self):
        self.assertEqual(score_to_tier(20), "Bronze")
        self.assertEqual(score_to_tier(39), "Bronze")

    def test_silver(self):
        self.assertEqual(score_to_tier(40), "Silver")
        self.assertEqual(score_to_tier(59), "Silver")

    def test_gold(self):
        self.assertEqual(score_to_tier(60), "Gold")
        self.assertEqual(score_to_tier(79), "Gold")

    def test_platinum(self):
        self.assertEqual(score_to_tier(80), "Platinum")
        self.assertEqual(score_to_tier(95), "Platinum")


class TestBondTierPoints(unittest.TestCase):

    def test_no_stake(self):
        tier, pts = bond_tier_points(0)
        self.assertEqual(tier, "None")
        self.assertEqual(pts, 0)

    def test_bronze(self):
        tier, pts = bond_tier_points(BRONZE_THRESHOLD)
        self.assertEqual(tier, "Bronze")
        self.assertEqual(pts, 5)

    def test_silver(self):
        tier, pts = bond_tier_points(SILVER_THRESHOLD)
        self.assertEqual(tier, "Silver")
        self.assertEqual(pts, 10)

    def test_gold(self):
        tier, pts = bond_tier_points(GOLD_THRESHOLD)
        self.assertEqual(tier, "Gold")
        self.assertEqual(pts, 15)

    def test_platinum(self):
        tier, pts = bond_tier_points(PLATINUM_THRESHOLD)
        self.assertEqual(tier, "Platinum")
        self.assertEqual(pts, 20)

    def test_below_bronze(self):
        tier, pts = bond_tier_points(Web3.to_wei(0.001, "ether"))
        self.assertEqual(tier, "None")
        self.assertEqual(pts, 0)


class TestCalculateStreetCred(unittest.TestCase):

    def test_unregistered_no_bonds(self):
        sb = calculate_street_cred(is_registered=False, bonds=[])
        self.assertEqual(sb.total, 0)
        self.assertEqual(sb.tier, "Unranked")
        self.assertEqual(sb.identity_points, 0)

    def test_registered_no_bonds(self):
        sb = calculate_street_cred(is_registered=True, bonds=[])
        self.assertEqual(sb.identity_points, 30)
        self.assertEqual(sb.bond_points, 0)
        self.assertEqual(sb.total, 30)
        self.assertEqual(sb.tier, "Bronze")

    def test_registered_with_inactive_bond(self):
        bonds = [{"active": False, "stakeAmount": GOLD_THRESHOLD}]
        sb = calculate_street_cred(is_registered=True, bonds=bonds)
        self.assertEqual(sb.identity_points, 30)
        self.assertEqual(sb.bond_points, 25)
        self.assertEqual(sb.active_bond_points, 0)
        self.assertEqual(sb.tier_points, 15)  # Gold tier
        self.assertEqual(sb.total, 30 + 25 + 0 + 15)
        self.assertEqual(sb.tier, "Silver")

    def test_registered_with_active_platinum_bond(self):
        bonds = [{"active": True, "stakeAmount": PLATINUM_THRESHOLD}]
        sb = calculate_street_cred(is_registered=True, bonds=bonds)
        self.assertEqual(sb.identity_points, 30)
        self.assertEqual(sb.bond_points, 25)
        self.assertEqual(sb.active_bond_points, 15)
        self.assertEqual(sb.tier_points, 20)
        self.assertEqual(sb.total, 90)
        self.assertEqual(sb.tier, "Platinum")

    def test_multiple_bonds_bonus(self):
        bonds = [
            {"active": True, "stakeAmount": BRONZE_THRESHOLD},
            {"active": False, "stakeAmount": BRONZE_THRESHOLD},
        ]
        sb = calculate_street_cred(is_registered=True, bonds=bonds)
        self.assertEqual(sb.multi_bond_points, 5)

    def test_max_score_95(self):
        # Identity (30) + bond (25) + active (15) + platinum (20) + multi (5) = 95
        bonds = [
            {"active": True, "stakeAmount": PLATINUM_THRESHOLD},
            {"active": True, "stakeAmount": BRONZE_THRESHOLD},
        ]
        sb = calculate_street_cred(is_registered=True, bonds=bonds)
        self.assertEqual(sb.total, 95)
        self.assertEqual(sb.tier, "Platinum")

    def test_score_breakdown_dict(self):
        bonds = [{"active": True, "stakeAmount": GOLD_THRESHOLD}]
        sb = calculate_street_cred(is_registered=True, bonds=bonds)
        d = sb.to_dict()
        self.assertIn("total", d)
        self.assertIn("tier", d)
        self.assertIn("breakdown", d)
        self.assertIn("bond_stake_tier", d)
        self.assertIn("details", d)
        self.assertIsInstance(d["details"], list)


# ---------------------------------------------------------------------------
# Chain config tests (no network required)
# ---------------------------------------------------------------------------

from vaultfire_crewai.chains import get_chain, SUPPORTED_CHAINS, ChainConfig


class TestChainConfig(unittest.TestCase):

    def test_supported_chains_exist(self):
        self.assertIn("base", SUPPORTED_CHAINS)
        self.assertIn("avalanche", SUPPORTED_CHAINS)
        self.assertIn("arbitrum", SUPPORTED_CHAINS)
        self.assertIn("polygon", SUPPORTED_CHAINS)

    def test_get_chain_base(self):
        cfg = get_chain("base")
        self.assertIsInstance(cfg, ChainConfig)
        self.assertEqual(cfg.chain_id, 8453)
        self.assertEqual(cfg.name, "Base")

    def test_get_chain_avalanche(self):
        cfg = get_chain("avalanche")
        self.assertEqual(cfg.chain_id, 43114)

    def test_get_chain_arbitrum(self):
        cfg = get_chain("arbitrum")
        self.assertEqual(cfg.chain_id, 42161)

    def test_get_chain_polygon(self):
        cfg = get_chain("polygon")
        self.assertEqual(cfg.chain_id, 137)

    def test_get_chain_case_insensitive(self):
        cfg = get_chain("BASE")
        self.assertEqual(cfg.chain_id, 8453)

    def test_get_chain_invalid(self):
        with self.assertRaises(ValueError):
            get_chain("solana")

    def test_contract_addresses_non_empty(self):
        cfg = get_chain("base")
        self.assertTrue(cfg.contracts.identity.startswith("0x"))
        self.assertTrue(cfg.contracts.partnership.startswith("0x"))
        self.assertTrue(cfg.contracts.reputation.startswith("0x"))
        self.assertTrue(cfg.contracts.bridge.startswith("0x"))

    def test_arbitrum_polygon_share_addresses(self):
        arb = get_chain("arbitrum")
        poly = get_chain("polygon")
        self.assertEqual(arb.contracts.identity, poly.contracts.identity)
        self.assertEqual(arb.contracts.partnership, poly.contracts.partnership)


# ---------------------------------------------------------------------------
# VaultfireClient initialization tests (mocked web3)
# ---------------------------------------------------------------------------

from vaultfire_crewai.client import VaultfireClient


class TestVaultfireClientInit(unittest.TestCase):

    @patch("vaultfire_crewai.client.Web3")
    def test_init_default_chain(self, MockWeb3):
        mock_w3 = MagicMock()
        MockWeb3.return_value = mock_w3
        MockWeb3.HTTPProvider = MagicMock()
        client = VaultfireClient()
        self.assertEqual(client.chain_config.name, "Base")

    @patch("vaultfire_crewai.client.Web3")
    def test_init_avalanche(self, MockWeb3):
        mock_w3 = MagicMock()
        MockWeb3.return_value = mock_w3
        MockWeb3.HTTPProvider = MagicMock()
        client = VaultfireClient(chain="avalanche")
        self.assertEqual(client.chain_config.chain_id, 43114)

    @patch("vaultfire_crewai.client.Web3")
    def test_custom_rpc_url(self, MockWeb3):
        mock_w3 = MagicMock()
        MockWeb3.return_value = mock_w3
        MockWeb3.HTTPProvider = MagicMock()
        custom_rpc = "https://my-custom-node.example.com"
        client = VaultfireClient(chain="base", rpc_url=custom_rpc)
        self.assertEqual(client._rpc_url, custom_rpc)

    def test_invalid_chain_raises(self):
        with self.assertRaises(ValueError):
            VaultfireClient(chain="fantom")


# ---------------------------------------------------------------------------
# verify_trust structure test (fully mocked)
# ---------------------------------------------------------------------------

class TestVerifyTrustMocked(unittest.TestCase):

    def _make_client_with_mocks(
        self,
        chain: str = "base",
        is_registered: bool = True,
        bonds=None,
    ):
        """Create a VaultfireClient with all contract calls mocked."""
        bonds = bonds or []
        client = VaultfireClient.__new__(VaultfireClient)
        client.chain_config = get_chain(chain)
        client._rpc_url = client.chain_config.rpc_url
        client._identity_contract = None
        client._partnership_contract = None
        client._reputation_contract = None
        client._bridge_contract = None

        # Patch individual methods
        client.get_agent = MagicMock(
            return_value={
                "address": "0xfA15Ee28939B222B0448261A22156070f0A7813C",
                "agentURI": "ipfs://Qmtest" if is_registered else "",
                "active": is_registered,
                "agentType": "researcher",
                "registeredAt": 1700000000,
            }
        )
        client.get_bonds_by_participant = MagicMock(return_value=bonds)
        client.get_reputation = MagicMock(
            return_value={
                "address": "0xfA15Ee28939B222B0448261A22156070f0A7813C",
                "averageRating": 90,
                "totalFeedbacks": 5,
                "verifiedFeedbacks": 3,
                "lastUpdated": 1700000000,
            }
        )
        client.is_agent_recognized = MagicMock(return_value=True)
        return client

    def test_trusted_verdict_with_score(self):
        bonds = [{"active": True, "stakeAmount": GOLD_THRESHOLD}]
        client = self._make_client_with_mocks(bonds=bonds)
        result = client.verify_trust(
            "0xfA15Ee28939B222B0448261A22156070f0A7813C", min_score=20
        )
        self.assertIn("verdict", result)
        self.assertEqual(result["verdict"], "TRUSTED")
        self.assertTrue(result["trusted"])
        self.assertIn("street_cred", result)
        self.assertIn("total", result["street_cred"])

    def test_untrusted_verdict_when_below_min_score(self):
        client = self._make_client_with_mocks(is_registered=False, bonds=[])
        result = client.verify_trust(
            "0xfA15Ee28939B222B0448261A22156070f0A7813C", min_score=50
        )
        self.assertEqual(result["verdict"], "UNTRUSTED")
        self.assertFalse(result["trusted"])

    def test_result_contains_required_keys(self):
        client = self._make_client_with_mocks()
        result = client.verify_trust("0xfA15Ee28939B222B0448261A22156070f0A7813C")
        for key in (
            "address", "chain", "chain_id", "verdict", "trusted",
            "min_score_required", "street_cred", "identity", "bonds",
            "reputation", "bridge_recognized", "timestamp",
        ):
            self.assertIn(key, result, f"Missing key: {key}")


# ---------------------------------------------------------------------------
# get_protocol_stats test (mocked)
# ---------------------------------------------------------------------------

class TestProtocolStatsMocked(unittest.TestCase):

    def test_stats_structure(self):
        client = VaultfireClient.__new__(VaultfireClient)
        client.chain_config = get_chain("base")
        client.get_total_agents = MagicMock(return_value=42)
        client.get_next_bond_id = MagicMock(return_value=100)
        client.get_total_active_bond_value = MagicMock(
            return_value=Web3.to_wei(5.5, "ether")
        )
        client.get_synced_agent_count = MagicMock(return_value=38)

        stats = client.get_protocol_stats()

        self.assertEqual(stats["total_agents"], 42)
        self.assertEqual(stats["next_bond_id"], 100)
        self.assertEqual(stats["total_bonds"], 99)
        self.assertAlmostEqual(stats["total_active_bond_value_eth"], 5.5, places=4)
        self.assertEqual(stats["synced_agent_count"], 38)
        self.assertIn("timestamp", stats)


if __name__ == "__main__":
    unittest.main()
