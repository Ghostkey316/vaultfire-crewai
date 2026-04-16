"""
Street Cred scoring logic for Vaultfire Protocol.

Street Cred is a composite on-chain trust score (0-95) that aggregates:
  - Identity registration status
  - Partnership bond existence and activity
  - Bond stake tier
  - Multi-bond diversification

Scoring breakdown:
  Identity Registered  : 30 pts
  Has Bond             : 25 pts
  Bond Active          : 15 pts
  Bond Tier            : 0-20 pts  (based on highest stake)
  Multiple Bonds       : 5 pts
  ─────────────────────────────
  Maximum              : 95 pts

Tiers:
  Unranked  :  0 – 19
  Bronze    : 20 – 39
  Silver    : 40 – 59
  Gold      : 60 – 79
  Platinum  : 80 – 95
"""

from dataclasses import dataclass, field
from typing import List, Optional
from web3 import Web3


# ------------------------------------------------------------------
# Bond tier thresholds (in Wei — ETH/native token)
# ------------------------------------------------------------------

PLATINUM_THRESHOLD = Web3.to_wei(0.5, "ether")   # ≥ 0.5 ETH → 20 pts
GOLD_THRESHOLD     = Web3.to_wei(0.1, "ether")   # ≥ 0.1 ETH → 15 pts
SILVER_THRESHOLD   = Web3.to_wei(0.05, "ether")  # ≥ 0.05 ETH → 10 pts
BRONZE_THRESHOLD   = Web3.to_wei(0.01, "ether")  # ≥ 0.01 ETH →  5 pts


def bond_tier_points(stake_amount_wei: int) -> tuple[str, int]:
    """Return (tier_name, points) for a given stake amount in Wei."""
    if stake_amount_wei >= PLATINUM_THRESHOLD:
        return "Platinum", 20
    if stake_amount_wei >= GOLD_THRESHOLD:
        return "Gold", 15
    if stake_amount_wei >= SILVER_THRESHOLD:
        return "Silver", 10
    if stake_amount_wei >= BRONZE_THRESHOLD:
        return "Bronze", 5
    return "None", 0


# ------------------------------------------------------------------
# Score tier thresholds (by final score)
# ------------------------------------------------------------------

SCORE_TIERS = [
    (80, "Platinum"),
    (60, "Gold"),
    (40, "Silver"),
    (20, "Bronze"),
    (0,  "Unranked"),
]


def score_to_tier(score: int) -> str:
    """Map a Street Cred score to its tier label."""
    for threshold, tier in SCORE_TIERS:
        if score >= threshold:
            return tier
    return "Unranked"


# ------------------------------------------------------------------
# Score breakdown dataclass
# ------------------------------------------------------------------

@dataclass
class ScoreBreakdown:
    identity_points: int = 0
    bond_points: int = 0
    active_bond_points: int = 0
    tier_points: int = 0
    multi_bond_points: int = 0
    total: int = 0
    tier: str = "Unranked"
    bond_stake_tier: str = "None"
    details: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "tier": self.tier,
            "breakdown": {
                "identity_registered": self.identity_points,
                "has_bond": self.bond_points,
                "bond_active": self.active_bond_points,
                "bond_stake_tier": self.tier_points,
                "multiple_bonds": self.multi_bond_points,
            },
            "bond_stake_tier": self.bond_stake_tier,
            "details": self.details,
        }


# ------------------------------------------------------------------
# Scoring function
# ------------------------------------------------------------------

def calculate_street_cred(
    is_registered: bool,
    bonds: Optional[List[dict]] = None,
) -> ScoreBreakdown:
    """
    Calculate Street Cred score from on-chain data.

    Parameters
    ----------
    is_registered:
        Whether the address has a registered identity on-chain.
    bonds:
        List of bond dicts with at least {'active': bool, 'stakeAmount': int}.
        stakeAmount should be in Wei.

    Returns
    -------
    ScoreBreakdown with full point breakdown and tier.
    """
    bonds = bonds or []
    sb = ScoreBreakdown()

    # 1. Identity registered (30 pts)
    if is_registered:
        sb.identity_points = 30
        sb.details.append("✓ Identity registered on-chain (+30)")
    else:
        sb.details.append("✗ No on-chain identity registered (0)")

    # 2. Has at least one bond (25 pts)
    if bonds:
        sb.bond_points = 25
        sb.details.append(f"✓ Has {len(bonds)} partnership bond(s) (+25)")
    else:
        sb.details.append("✗ No partnership bonds (0)")

    # 3. Has an active bond (15 pts)
    active_bonds = [b for b in bonds if b.get("active", False)]
    if active_bonds:
        sb.active_bond_points = 15
        sb.details.append(f"✓ {len(active_bonds)} active bond(s) (+15)")
    elif bonds:
        sb.details.append("✗ No active bonds (0)")

    # 4. Bond tier by highest stake (up to 20 pts)
    if bonds:
        max_stake = max(b.get("stakeAmount", 0) for b in bonds)
        tier_name, tier_pts = bond_tier_points(max_stake)
        sb.tier_points = tier_pts
        sb.bond_stake_tier = tier_name
        eth_amount = Web3.from_wei(max_stake, "ether")
        if tier_pts > 0:
            sb.details.append(
                f"✓ Highest bond stake: {eth_amount} ETH ({tier_name} tier, +{tier_pts})"
            )
        else:
            sb.details.append(
                f"✗ Bond stake too low for tier: {eth_amount} ETH (0)"
            )

    # 5. Multiple bonds (5 pts)
    if len(bonds) > 1:
        sb.multi_bond_points = 5
        sb.details.append(f"✓ Multiple bonds ({len(bonds)}) (+5)")

    # Total
    sb.total = (
        sb.identity_points
        + sb.bond_points
        + sb.active_bond_points
        + sb.tier_points
        + sb.multi_bond_points
    )
    sb.tier = score_to_tier(sb.total)

    return sb
