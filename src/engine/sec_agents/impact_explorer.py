from agents import Agent, ModelSettings, Runner
from agents.model_settings import Reasoning

from engine.models.app_breakdown import ApplicationCapabilityAnalysis
from engine.models.attack_paths import (
    ImpactExplorerInput,
    ImpactExplorerOutput,
)
from engine.prompts.impact_explorer import IMPACT_EXPLORER_PROMPT
from engine.sec_agents.capability_search import create_capability_search_agent
from engine.tools.crawling import get_page_content_as_markdown, list_links_on_page
from engine.tools.environment_search import get_environment_constraints_tool
from engine.tools.mitre_attack import (
    get_all_mitre_tactics,
    get_examples_of_technique_for_saas_from_mitre,
    list_all_mitre_techniques_by_tactic_for_saas,
)


def create_impact_explorer_agent(
    application_capabilities: ApplicationCapabilityAnalysis,
):
    """Create an impact explorer agent that discovers all impact vectors.

    This factory function creates an agent that can systematically discover all
    plausible impact methods an attacker could use after gaining prerequisite access.

    Args:
        application_capabilities: The full application capability analysis
    """
    # Create the capability search agent as a tool
    capability_search_tool = create_capability_search_agent(application_capabilities)

    # Create the Impact Explorer Agent
    impact_explorer_agent = Agent(
        name="impact-explorer-agent",
        model="gpt-5.1",
        instructions=IMPACT_EXPLORER_PROMPT,
        output_type=ImpactExplorerOutput,
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

    return impact_explorer_agent


async def run_impact_exploration(
    application_capabilities: ApplicationCapabilityAnalysis,
    objective: str | None = None,
) -> ImpactExplorerOutput:
    """
    Run the impact exploration workflow.

    This function discovers all plausible impact vectors for an application
    by systematically evaluating MITRE ATT&CK Impact techniques against
    the application's documented capabilities, starting from a given prerequisite vector.

    Args:
        application_capabilities: Complete application capability analysis
        objective: Optional specific attacker objective that may inform which
                   impact methods are most relevant

    Returns:
        ImpactExplorerOutput with all discovered impact vectors
    """
    # Create the impact explorer agent
    impact_explorer_agent = create_impact_explorer_agent(
        application_capabilities
    )

    # Prepare input
    input_data = ImpactExplorerInput(
        application_capabilities=application_capabilities,
        objective=objective,
    )

    # Run the agent
    print("Running impact exploration...")
    result = await Runner.run(
        impact_explorer_agent,
        input_data.model_dump_json(),
        max_turns=200,
    )

    return result.final_output

