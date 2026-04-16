"""
vaultfire-crewai — CrewAI tools for Vaultfire Protocol trust verification.

Quick start:
    from vaultfire_crewai import vaultfire_verify_agent, vaultfire_get_street_cred

    researcher = Agent(
        role="Trust Analyst",
        goal="Verify AI agent trustworthiness",
        tools=[vaultfire_verify_agent, vaultfire_get_street_cred],
    )

All tools can also be imported from vaultfire_crewai.tools.
"""

from .tools import (
    vaultfire_verify_agent,
    vaultfire_get_street_cred,
    vaultfire_get_agent,
    vaultfire_get_bonds,
    vaultfire_get_reputation,
    vaultfire_discover_agents,
    vaultfire_protocol_stats,
    vaultfire_register_agent,
    vaultfire_create_bond,
    ALL_TOOLS,
)

from .client import VaultfireClient
from .chains import CHAINS, SUPPORTED_CHAINS, DEFAULT_CHAIN, get_chain
from .scoring import calculate_street_cred, ScoreBreakdown, score_to_tier

__version__ = "1.0.0"
__author__ = "Ghostkey316"

__all__ = [
    # CrewAI tools
    "vaultfire_verify_agent",
    "vaultfire_get_street_cred",
    "vaultfire_get_agent",
    "vaultfire_get_bonds",
    "vaultfire_get_reputation",
    "vaultfire_discover_agents",
    "vaultfire_protocol_stats",
    "vaultfire_register_agent",
    "vaultfire_create_bond",
    "ALL_TOOLS",
    # Core classes
    "VaultfireClient",
    # Chain utilities
    "CHAINS",
    "SUPPORTED_CHAINS",
    "DEFAULT_CHAIN",
    "get_chain",
    # Scoring utilities
    "calculate_street_cred",
    "ScoreBreakdown",
    "score_to_tier",
    # Package metadata
    "__version__",
    "__author__",
]
