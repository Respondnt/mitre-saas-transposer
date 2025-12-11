# MITRE SaaS Transposer

A security analysis tool that automatically analyzes SaaS applications and generates comprehensive attack paths mapped to the MITRE ATT&CK framework. This tool uses AI agents to crawl application documentation, identify capabilities, and explore potential attack vectors across all MITRE ATT&CK tactics.

## Why

In a few of my previous roles we had to deeply threat-model SaaS apps we depended on — mapping how they work, where they can be abused, what telemetry they emit, and what detection coverage realistically looks like.

Anyone who’s done this knows it’s tedious and fragmented:
	•	Reading every docs page
	•	Enumerating functionality and admin surfaces
	•	Mapping those behaviours to MITRE ATT&CK
	•	Manually deriving initial access vectors and misuse paths
	•	Identifying where detection is/ isn’t possible

Every team does this from scratch, and it burns an insane amount of analyst time.

I wanted to see if I could automate the synthesis, not the judgement — i.e., have an agent greedily explore a SaaS app’s documentation and output a structured capability map + aligned MITRE techniques.


## Overview

MITRE SaaS Transposer performs automated threat modeling for SaaS applications by:

1. **Application Capability Discovery**: Crawls and analyzes application documentation to build a comprehensive map of features, APIs, integrations, and security-relevant behaviors
2. **Attack Path Generation**: Uses specialized AI agents to explore attack scenarios across all MITRE ATT&CK tactics:
   - Initial Access
   - Execution
   - Persistence
   - Privilege Escalation
   - Defense Evasion
   - Credential Access
   - Discovery
   - Lateral Movement
   - Collection
   - Command and Control
   - Exfiltration
   - Impact
3. **Threat Modeling**: Generates detailed attack paths with step-by-step methods, specific capabilities used, interfaces targeted, and detection considerations

## Architecture

The tool uses a multi-agent architecture:

- **App Breakdown Agent**: Analyzes application documentation to extract capabilities, features, APIs, and security-relevant behaviors
- **Tactic Explorer Agents**: Specialized agents for each MITRE ATT&CK tactic that explore attack scenarios in parallel

## Dependencies

This project currently depends on:

- **OpenAI**: Used for AI agent orchestration and reasoning. The agents use OpenAI's API for generating attack paths and analyzing application capabilities.
- **Firecrawl**: Used for web crawling and content extraction from application documentation sites.

**Note**: While the current implementation uses OpenAI and Firecrawl, the architecture is designed to be modular and could be modified to support other model providers (e.g., Anthropic Claude, Google Gemini, open-source models) and alternative web crawling solutions.

## Installation

```bash
# Install dependencies
uv sync

# Set up environment variables
export OPENAI_API_KEY="your-api-key"
```

## Usage

```python
from engine.runner.run import run_analysis

# Run comprehensive analysis
results = await run_analysis(objective="Analyze security posture")

# Or run individual components
from engine.sec_agents.app_breakdown import run_app_breakdown
from engine.sec_agents.attack_path_generation import run_attack_path_generation

# Analyze application capabilities
app_capabilities = await run_app_breakdown(
    app_urls=["https://example.com"],
    relevant_sitemap_urls=["https://example.com/sitemap.xml"]
)

# Generate attack paths
attack_paths = await run_attack_path_generation(app_capabilities)
```

## Project Structure

```
src/engine/
├── models/          # Pydantic models for data structures
├── prompts/         # Agent prompts and instructions
├── sec_agents/      # Security analysis agents
├── tools/           # Utility tools (MITRE ATT&CK, crawling, etc.)
└── runner/          # Main execution entry point
```

## Features

- **Comprehensive Documentation Analysis**: Systematically explores application documentation using sitemaps and hierarchical crawling
- **MITRE ATT&CK Integration**: Maps findings to the official MITRE ATT&CK framework for SaaS platforms
- **Parallel Analysis**: Explores multiple attack tactics simultaneously for efficiency
- **Structured Output**: Generates detailed, structured attack paths with detection considerations
- **Capability Mapping**: Creates a complete capability map of application features and behaviors

## License

See LICENSE file for details.

