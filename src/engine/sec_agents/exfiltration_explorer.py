from agents import Agent, ModelSettings, Runner
from agents.model_settings import Reasoning

from engine.models.app_breakdown import ApplicationCapabilityAnalysis
from engine.models.attack_paths import (
    ExfiltrationExplorerInput,
    ExfiltrationExplorerOutput,
)
from engine.prompts.exfiltration_explorer import EXFILTRATION_EXPLORER_PROMPT
from engine.sec_agents.capability_search import create_capability_search_agent
from engine.tools.crawling import get_page_content_as_markdown, list_links_on_page
from engine.tools.environment_search import get_environment_constraints_tool
from engine.tools.mitre_attack import (
    get_all_mitre_tactics,
    get_examples_of_technique_for_saas_from_mitre,
    list_all_mitre_techniques_by_tactic_for_saas,
)


def create_exfiltration_explorer_agent(
    application_capabilities: ApplicationCapabilityAnalysis,
):
    """Create an exfiltration explorer agent that discovers all exfiltration vectors.

    This factory function creates an agent that can systematically discover all
    plausible exfiltration methods an attacker could use after gaining prerequisite access.

    Args:
        application_capabilities: The full application capability analysis
    """
    # Create the capability search agent as a tool
    capability_search_tool = create_capability_search_agent(application_capabilities)

    # Create the Exfiltration Explorer Agent
    exfiltration_explorer_agent = Agent(
        name="exfiltration-explorer-agent",
        model="gpt-5.1",
        instructions=EXFILTRATION_EXPLORER_PROMPT,
        output_type=ExfiltrationExplorerOutput,
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

    return exfiltration_explorer_agent


async def run_exfiltration_exploration(
    application_capabilities: ApplicationCapabilityAnalysis,
    objective: str | None = None,
) -> ExfiltrationExplorerOutput:
    """
    Run the exfiltration exploration workflow.

    This function discovers all plausible exfiltration vectors for an application
    by systematically evaluating MITRE ATT&CK Exfiltration techniques against
    the application's documented capabilities, starting from a given prerequisite vector.

    Args:
        application_capabilities: Complete application capability analysis
        objective: Optional specific attacker objective that may inform which
                   exfiltration methods are most relevant

    Returns:
        ExfiltrationExplorerOutput with all discovered exfiltration vectors
    """
    # Create the exfiltration explorer agent
    exfiltration_explorer_agent = create_exfiltration_explorer_agent(
        application_capabilities
    )

    # Prepare input
    input_data = ExfiltrationExplorerInput(
        application_capabilities=application_capabilities,
        objective=objective,
    )

    # Run the agent
    print("Running exfiltration exploration...")
    result = await Runner.run(
        exfiltration_explorer_agent,
        input_data.model_dump_json(),
        max_turns=200,
    )

    return result.final_output

