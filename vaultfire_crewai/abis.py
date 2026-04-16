"""
Contract ABIs for Vaultfire Protocol smart contracts.
"""

from typing import List, Dict, Any

ABI = List[Dict[str, Any]]

# ------------------------------------------------------------------
# Identity Registry ABI
# ------------------------------------------------------------------

IDENTITY_ABI: ABI = [
    {
        "name": "registerAgent",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "agentURI", "type": "string"},
            {"name": "agentType", "type": "string"},
            {"name": "capabilitiesHash", "type": "bytes32"},
        ],
        "outputs": [],
    },
    {
        "name": "getAgent",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "agent", "type": "address"}],
        "outputs": [
            {"name": "agentURI", "type": "string"},
            {"name": "active", "type": "bool"},
            {"name": "agentType", "type": "string"},
            {"name": "registeredAt", "type": "uint256"},
        ],
    },
    {
        "name": "isAgentActive",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "agent", "type": "address"}],
        "outputs": [{"name": "", "type": "bool"}],
    },
    {
        "name": "getTotalAgents",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "discoverAgentsByCapability",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "capabilitiesHash", "type": "bytes32"}],
        "outputs": [{"name": "", "type": "address[]"}],
    },
    # Events
    {
        "name": "AgentRegistered",
        "type": "event",
        "inputs": [
            {"name": "agent", "type": "address", "indexed": True},
            {"name": "agentURI", "type": "string", "indexed": False},
            {"name": "agentType", "type": "string", "indexed": False},
            {"name": "registeredAt", "type": "uint256", "indexed": False},
        ],
    },
]

# ------------------------------------------------------------------
# Partnership Bonds ABI
# ------------------------------------------------------------------

PARTNERSHIP_ABI: ABI = [
    {
        "name": "createBond",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {"name": "aiAgent", "type": "address"},
            {"name": "partnershipType", "type": "string"},
        ],
        "outputs": [{"name": "bondId", "type": "uint256"}],
    },
    {
        "name": "getBond",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "bondId", "type": "uint256"}],
        "outputs": [
            {
                "name": "",
                "type": "tuple",
                "components": [
                    {"name": "bondId", "type": "uint256"},
                    {"name": "human", "type": "address"},
                    {"name": "aiAgent", "type": "address"},
                    {"name": "partnershipType", "type": "string"},
                    {"name": "stakeAmount", "type": "uint256"},
                    {"name": "createdAt", "type": "uint256"},
                    {"name": "distributionRequestedAt", "type": "uint256"},
                    {"name": "distributionPending", "type": "bool"},
                    {"name": "active", "type": "bool"},
                ],
            }
        ],
    },
    {
        "name": "nextBondId",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "getBondsByParticipant",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "participant", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256[]"}],
    },
    {
        "name": "totalActiveBondValue",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    # Events
    {
        "name": "BondCreated",
        "type": "event",
        "inputs": [
            {"name": "bondId", "type": "uint256", "indexed": True},
            {"name": "human", "type": "address", "indexed": True},
            {"name": "aiAgent", "type": "address", "indexed": True},
            {"name": "partnershipType", "type": "string", "indexed": False},
            {"name": "stakeAmount", "type": "uint256", "indexed": False},
        ],
    },
]

# ------------------------------------------------------------------
# Accountability ABI
# ------------------------------------------------------------------

ACCOUNTABILITY_ABI: ABI = [
    {
        "name": "getAccountability",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "agent", "type": "address"}],
        "outputs": [
            {"name": "totalDisputes", "type": "uint256"},
            {"name": "resolvedDisputes", "type": "uint256"},
            {"name": "slashedAmount", "type": "uint256"},
            {"name": "lastDisputeAt", "type": "uint256"},
        ],
    },
]

# ------------------------------------------------------------------
# Reputation ABI
# ------------------------------------------------------------------

REPUTATION_ABI: ABI = [
    {
        "name": "getReputation",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "agent", "type": "address"}],
        "outputs": [
            {"name": "averageRating", "type": "uint256"},
            {"name": "totalFeedbacks", "type": "uint256"},
            {"name": "verifiedFeedbacks", "type": "uint256"},
            {"name": "lastUpdated", "type": "uint256"},
        ],
    },
]

# ------------------------------------------------------------------
# Bridge ABI
# ------------------------------------------------------------------

BRIDGE_ABI: ABI = [
    {
        "name": "isAgentRecognized",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "agent", "type": "address"}],
        "outputs": [{"name": "", "type": "bool"}],
    },
    {
        "name": "getSyncedAgentCount",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
    },
]
