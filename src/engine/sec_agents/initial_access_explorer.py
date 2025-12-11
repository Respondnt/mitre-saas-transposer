from agents import Agent, ModelSettings, Runner
from agents.model_settings import Reasoning

from engine.models.app_breakdown import ApplicationCapabilityAnalysis
from engine.models.attack_paths import (
    InitialAccessExplorerInput,
    InitialAccessExplorerOutput,
)
from engine.prompts.initial_access_explorer import INITIAL_ACCESS_EXPLORER_PROMPT
from engine.sec_agents.capability_search import create_capability_search_agent
from engine.tools.crawling import get_page_content_as_markdown, list_links_on_page
from engine.tools.environment_search import get_environment_constraints_tool
from engine.tools.mitre_attack import (
    get_all_mitre_tactics,
    get_examples_of_technique_for_saas_from_mitre,
    list_all_mitre_techniques_by_tactic_for_saas,
)


def create_initial_access_explorer_agent(
    application_capabilities: ApplicationCapabilityAnalysis,
):
    """Create an initial access explorer agent that discovers all initial access vectors.

    This factory function creates an agent that can systematically discover all
    plausible initial access entry points for an application using MITRE ATT&CK
    Initial Access techniques.

    Args:
        application_capabilities: The full application capability analysis
    """
    # Create the capability search agent as a tool
    capability_search_tool = create_capability_search_agent(application_capabilities)

    # Create the Initial Access Explorer Agent
    initial_access_explorer_agent = Agent(
        name="initial-access-explorer-agent",
        model="gpt-5.1",
        instructions=INITIAL_ACCESS_EXPLORER_PROMPT,
        output_type=InitialAccessExplorerOutput,
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
            get_environment_constraints_tool,
            list_links_on_page,
            get_page_content_as_markdown,
        ],
    )

    return initial_access_explorer_agent


async def run_initial_access_exploration(
    application_capabilities: ApplicationCapabilityAnalysis,
    objective: str | None = None,
) -> InitialAccessExplorerOutput:
    """
    Run the initial access exploration workflow.

    This function discovers all plausible initial access vectors for an application
    by systematically evaluating MITRE ATT&CK Initial Access techniques against
    the application's documented capabilities.

    Args:
        application_capabilities: Complete application capability analysis
        objective: Optional specific attacker objective that may inform which
                   initial access vectors are most relevant

    Returns:
        InitialAccessExplorerOutput with all discovered initial access vectors
    """
    # Create the initial access explorer agent
    initial_access_explorer_agent = create_initial_access_explorer_agent(
        application_capabilities
    )

    # Prepare input
    input_data = InitialAccessExplorerInput(
        application_capabilities=application_capabilities,
        objective=objective,
    )

    # Run the agent
    print("Running initial access exploration...")
    result = await Runner.run(
        initial_access_explorer_agent,
        input_data.model_dump_json(),
        max_turns=200,
    )

    return result.final_output
