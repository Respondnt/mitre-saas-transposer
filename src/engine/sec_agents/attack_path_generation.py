from agents import Agent, ModelSettings, Reasoning, Runner

from engine.models.app_breakdown import ApplicationCapabilityAnalysis
from engine.models.attack_paths import (
    AdversarialMethod,
    AttackPathGenerationInput,
    AttackPathOutput,
)
from engine.prompts.adverserial_agent import ADVERSARIAL_AGENT_PROMPT
from engine.prompts.adverserial_orchestrator import ADVERSERIAL_ORCHESTRATOR
from engine.sec_agents.capability_search import create_capability_search_agent
from engine.tools.mitre_attack import (
    get_all_mitre_tactics,
    get_examples_of_technique_for_saas_from_mitre,
    list_all_mitre_techniques_by_tactic_for_saas,
)


async def run_attack_path_generation(
    application_capabilities: ApplicationCapabilityAnalysis,
) -> AttackPathOutput:
    """[]
    Run the complete attack path generation workflow using the Manager pattern.

    This uses a three-agent architecture:
    1. Hypothesis Agent (Manager): Orchestrates the entire workflow
    2. Adversarial Agent (Child): Determines how to achieve each tactic

    The Hypothesis Agent invokes the other agents as tools and assembles
    the complete attack paths.

    Args:
        application_capabilities: Complete application capability analysis

    Returns:
        Complete attack path analysis with methods and detections
    """

    # Create the capability search agent as a tool
    capability_search_tool = create_capability_search_agent(application_capabilities)
    print("Created capability search tool")

    # Create the Adversarial Agent (child agent)
    adversarial_agent = Agent(
        name="adversarial-agent",
        model="gpt-5.1",
        instructions=ADVERSARIAL_AGENT_PROMPT,
        output_type=AdversarialMethod,
        model_settings=ModelSettings(
            reasoning=Reasoning(
                effort="high",
                summary="detailed",
            ),
            parallel_tool_calls=True,
        ),
        tools=[
            capability_search_tool,
            get_all_mitre_tactics,
            list_all_mitre_techniques_by_tactic_for_saas,
            get_examples_of_technique_for_saas_from_mitre,
        ],
    )

    # Create the Adverserial Orchestrator (manager) with child agents as tools
    adverserial_orchestrator = Agent(
        name="adverserial-orchestrator",
        model="gpt-5.1",
        instructions=ADVERSERIAL_ORCHESTRATOR,
        output_type=AttackPathOutput,
        model_settings=ModelSettings(
            reasoning=Reasoning(
                effort="high",
                summary="detailed",
            ),
            parallel_tool_calls=True,
        ),
        tools=[
            capability_search_tool,
            adversarial_agent.as_tool(
                tool_name="adversarial_agent",
                tool_description=(
                    "Determines HOW an attacker would achieve a specific MITRE ATT&CK tactic "
                    "using the application's capabilities. Call this for each tactic in an attack chain "
                    "to get detailed adversarial methods. Input: scenario_description, tactic_to_achieve, "
                    "preconditions. Output: AdversarialMethod with step-by-step method_steps, specific capabilities, interfaces, and evasion considerations."
                ),
                max_turns=25,
            ),
        ],
    )

    # Run the manager agent asynchronously - it will orchestrate everything with parallel tool calls
    result = await Runner.run(
        adverserial_orchestrator,
        AttackPathGenerationInput(
            application_capabilities=application_capabilities,
        ).model_dump_json(),
        max_turns=150,
    )

    return result.final_output
