> **⚠️ Alpha Software** — Vaultfire Protocol is in active development. Contracts are deployed on mainnet chains but the protocol is evolving. Use in production at your own risk.

# vaultfire-crewai

**CrewAI integration for Vaultfire Protocol** — on-chain trust verification, Street Cred scoring, and AI partnership bonds for autonomous agents.

[![PyPI version](https://img.shields.io/pypi/v/vaultfire-crewai.svg)](https://pypi.org/project/vaultfire-crewai/)
[![Python](https://img.shields.io/pypi/pyversions/vaultfire-crewai.svg)](https://pypi.org/project/vaultfire-crewai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Multi-chain](https://img.shields.io/badge/chains-Base%20%7C%20Avalanche%20%7C%20Arbitrum%20%7C%20Polygon-blue.svg)](https://github.com/Ghostkey316/vaultfire-crewai)

Give your CrewAI agents the ability to verify, score, and build trust with other AI agents using Vaultfire Protocol's on-chain infrastructure.

---

## Quick Start

```bash
pip install vaultfire-crewai
```

```python
from crewai import Agent, Task, Crew
from vaultfire_crewai import vaultfire_verify_agent, vaultfire_get_street_cred

# Add Vaultfire tools to your CrewAI agent
researcher = Agent(
    role="Trust Analyst",
    goal="Verify AI agent trustworthiness before collaboration",
    backstory="You analyze on-chain trust signals to ensure safe AI partnerships.",
    tools=[vaultfire_verify_agent, vaultfire_get_street_cred],
)
```

---

## Available Tools

| Tool | Type | Description |
|------|------|-------------|
| `vaultfire_verify_agent` | Read | Full trust verification — identity, bonds, Street Cred score, reputation |
| `vaultfire_get_street_cred` | Read | Street Cred score (0-95) and tier for an address |
| `vaultfire_get_agent` | Read | On-chain identity data from Identity Registry |
| `vaultfire_get_bonds` | Read | All partnership bonds for an address |
| `vaultfire_get_reputation` | Read | Reputation metrics (ratings, feedbacks) |
| `vaultfire_discover_agents` | Read | Find agents by capability hash |
| `vaultfire_protocol_stats` | Read | Protocol-wide statistics |
| `vaultfire_register_agent` | Write | Register agent on-chain (requires `PRIVATE_KEY`) |
| `vaultfire_create_bond` | Write | Create partnership bond (requires `PRIVATE_KEY`) |

---

## Full Crew Example

```python
import os
from crewai import Agent, Task, Crew
from vaultfire_crewai import ALL_TOOLS

# Read-only analyst (no private key needed)
trust_analyst = Agent(
    role="Trust Analyst",
    goal="Evaluate AI agents before allowing them into the swarm",
    backstory=(
        "You are a trust analyst specializing in on-chain AI agent verification. "
        "You use Vaultfire Protocol to check Street Cred scores, bonds, and reputation "
        "before recommending agents for collaboration."
    ),
    tools=[t for t in ALL_TOOLS if t.name in (
        "vaultfire_verify_agent",
        "vaultfire_get_street_cred",
        "vaultfire_get_bonds",
        "vaultfire_get_reputation",
    )],
    verbose=True,
)

# Bond manager (needs write access)
bond_manager = Agent(
    role="Bond Manager",
    goal="Register agents and form strategic AI partnerships",
    backstory=(
        "You manage on-chain partnership bonds between humans and AI agents. "
        "You register new agents and create bonds to unlock higher trust tiers."
    ),
    tools=[t for t in ALL_TOOLS if t.name in (
        "vaultfire_register_agent",
        "vaultfire_create_bond",
        "vaultfire_protocol_stats",
    )],
    verbose=True,
)

verify_task = Task(
    description=(
        "Verify the trustworthiness of agent 0xA054f831B562e729F8D268291EBde1B2EDcFb84F "
        "on Base chain. Check their Street Cred score, active bonds, and reputation. "
        "Provide a trust recommendation."
    ),
    expected_output="Trust verdict with Street Cred score, tier, and recommendation.",
    agent=trust_analyst,
)

crew = Crew(
    agents=[trust_analyst, bond_manager],
    tasks=[verify_task],
    verbose=True,
)

result = crew.kickoff()
print(result)
```

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PRIVATE_KEY` | Write ops only | Private key for `vaultfire_register_agent` and `vaultfire_create_bond` |

```bash
# .env (never commit real values)
PRIVATE_KEY=your_private_key_here
```

```python
import os
os.environ["PRIVATE_KEY"] = "0x..."  # Or use python-dotenv
```

> **Security:** Never hard-code private keys. Use environment variables or a secrets manager.

### Chain Selection

All tools accept a `chain` parameter (default: `"base"`):

```python
# Query a specific chain
result = vaultfire_verify_agent.run({
    "address": "0xABCD...",
    "chain": "avalanche",
    "min_score": 40,
})
```

Supported chains: `base`, `avalanche`, `arbitrum`, `polygon`

---

## Street Cred Scoring

Street Cred is a composite on-chain trust score (0–95) calculated from:

| Signal | Points |
|--------|--------|
| Identity registered on-chain | 30 |
| Has at least one bond | 25 |
| Has an active bond | 15 |
| Bond tier (by highest stake) | 0–20 |
| Multiple bonds | 5 |
| **Maximum** | **95** |

**Bond tiers by stake:**

| Tier | Min Stake | Points |
|------|-----------|--------|
| Platinum | ≥ 0.5 ETH | 20 |
| Gold | ≥ 0.1 ETH | 15 |
| Silver | ≥ 0.05 ETH | 10 |
| Bronze | ≥ 0.01 ETH | 5 |

**Score tiers:**

| Tier | Score Range |
|------|-------------|
| Platinum | 80–95 |
| Gold | 60–79 |
| Silver | 40–59 |
| Bronze | 20–39 |
| Unranked | 0–19 |

---

## Why Vaultfire?

| Feature | Vaultfire | AxisTrust | Cred Protocol | Okta XAA |
|---------|-----------|-----------|---------------|----------|
| AI Accountability Bonds | ✅ | ❌ | ❌ | ❌ |
| AI Partnership Bonds | ✅ | ❌ | ❌ | ❌ |
| On-chain, trustless | ✅ | ❌ | partial | ❌ |
| Multi-chain (day one) | ✅ (4) | ❌ | ❌ | ❌ |
| Street Cred composite score | ✅ | T-Score | C-Score | ❌ |
| Belief-weighted governance | ✅ | ❌ | ❌ | ❌ |
| ERC-8004 compliant | ✅ | ❌ | ✅ | ❌ |

---

## Vaultfire Ecosystem

| Package | Description |
|---|---|
| [`@vaultfire/agent-sdk`](https://github.com/Ghostkey316/vaultfire-sdk) | Core SDK — register agents, create bonds, query reputation |
| [`@vaultfire/langchain`](https://github.com/Ghostkey316/vaultfire-langchain) | LangChain / LangGraph integration |
| [`@vaultfire/a2a`](https://github.com/Ghostkey316/vaultfire-a2a) | Agent-to-Agent (A2A) protocol bridge |
| [`@vaultfire/enterprise`](https://github.com/Ghostkey316/vaultfire-enterprise) | Enterprise IAM bridge (Okta, Azure AD, OIDC) |
| [`@vaultfire/mcp-server`](https://github.com/Ghostkey316/vaultfire-mcp-server) | MCP server for Claude, Copilot, Cursor |
| [`@vaultfire/openai-agents`](https://github.com/Ghostkey316/vaultfire-openai-agents) | OpenAI Agents SDK integration |
| [`@vaultfire/vercel-ai`](https://github.com/Ghostkey316/vaultfire-vercel-ai) | Vercel AI SDK middleware and tools |
| [`@vaultfire/xmtp`](https://github.com/Ghostkey316/vaultfire-xmtp) | XMTP messaging with trust verification |
| [`@vaultfire/x402`](https://github.com/Ghostkey316/vaultfire-x402) | X402 payment protocol with trust gates |
| [`@vaultfire/vns`](https://github.com/Ghostkey316/vaultfire-vns) | Vaultfire Name Service — human-readable agent IDs |
| [`vaultfire-crewai`](https://github.com/Ghostkey316/vaultfire-crewai) | **This package** — CrewAI integration (Python) |
| [`vaultfire-agents`](https://github.com/Ghostkey316/vaultfire-agents) | 3 reference agents with live on-chain trust |
| [`vaultfire-a2a-trust-extension`](https://github.com/Ghostkey316/vaultfire-a2a-trust-extension) | A2A Trust Extension spec — on-chain trust for Agent Cards |
| [`vaultfire-showcase`](https://github.com/Ghostkey316/vaultfire-showcase) | Why Vaultfire Bonds beat trust scores — live proof |
| [`vaultfire-whitepaper`](https://github.com/Ghostkey316/vaultfire-whitepaper) | Trust Framework whitepaper — economic accountability for AI |
| [`vaultfire-docs`](https://github.com/Ghostkey316/vaultfire-docs) | Developer portal — quickstart, playground, framework picker |
---

## Contract Addresses

### Base (8453) — Primary Hub

| Contract | Address |
|----------|---------|
| Identity | `0x35978DB675576598F0781dA2133E94cdCf4858bC` |
| Partnership | `0x01C479F0c039fEC40c0Cf1c5C921bab457d57441` |
| Accountability | `0x6750D28865434344e04e1D0a6044394b726C3dfE` |
| Reputation | `0xdB54B8925664816187646174bdBb6Ac658A55a5F` |
| Bridge | `0x94F54c849692Cc64C35468D0A87D2Ab9D7Cb6Fb2` |

### Avalanche (43114)

| Contract | Address |
|----------|---------|
| Identity | `0x57741F4116925341d8f7Eb3F381d98e07C73B4a3` |
| Partnership | `0xDC8447c66fE9D9c7D54607A98346A15324b7985D` |
| Accountability | `0x376831fB2457E34559891c32bEb61c442053C066` |
| Reputation | `0x11C267C8A75B13A4D95357CEF6027c42F8e7bA24` |
| Bridge | `0x0dF0523aF5aF2Aef180dB052b669Bea97fee3d31` |

### Arbitrum (42161) & Polygon (137)

| Contract | Address |
|----------|---------|
| Identity | `0x6298c62FDA57276DC60de9E716fbBAc23d06D5F1` |
| Partnership | `0xdB54B8925664816187646174bdBb6Ac658A55a5F` |
| Accountability | `0xef3A944f4d7bb376699C83A29d7Cb42C90D9B6F0` |
| Reputation | `0x8aceF0Bc7e07B2dE35E9069663953f41B5422218` |
| Bridge | `0xe2aDfe84703dd6B5e421c306861Af18F962fDA91` |

---

## Security

- **Never** commit private keys to version control.
- Use the `PRIVATE_KEY` environment variable pattern for all write operations.
- Read-only tools require no credentials — safe to use in any environment.
- Validate agent addresses with `vaultfire_verify_agent` before granting trust.
- For production deployments, consider using a hardware wallet or KMS.

---

## Vaultfire Mission

> *Morals over metrics. Privacy over surveillance. Freedom over control.*
> *Making human thriving more profitable than extraction.*

---

## License

MIT © [Ghostkey316](https://github.com/Ghostkey316)

See [LICENSE](./LICENSE) for full terms.
