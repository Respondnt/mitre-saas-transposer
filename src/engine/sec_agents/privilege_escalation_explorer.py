from agents import Agent, ModelSettings, Runner
from agents.model_settings import Reasoning

from engine.models.app_breakdown import ApplicationCapabilityAnalysis
from engine.models.attack_paths import (
    PrivilegeEscalationExplorerInput,
    PrivilegeEscalationExplorerOutput,
)
from engine.prompts.privilege_escalation_explorer import PRIVILEGE_ESCALATION_EXPLORER_PROMPT
from engine.sec_agents.capability_search import create_capability_search_agent
from engine.tools.crawling import get_page_content_as_markdown, list_links_on_page
from engine.tools.environment_search import get_environment_constraints_tool
from engine.tools.mitre_attack import (
    get_all_mitre_tactics,
    get_examples_of_technique_for_saas_from_mitre,
    list_all_mitre_techniques_by_tactic_for_saas,
)


def create_privilege_escalation_explorer_agent(
    application_capabilities: ApplicationCapabilityAnalysis,
):
    """Create a privilege escalation explorer agent that discovers all privilege escalation vectors.

    This factory function creates an agent that can systematically discover all
    plausible privilege escalation methods an attacker could use after gaining prerequisite access.

    Args:
        application_capabilities: The full application capability analysis
    """
    # Create the capability search agent as a tool
    capability_search_tool = create_capability_search_agent(application_capabilities)

    # Create the Privilege Escalation Explorer Agent
    privilege_escalation_explorer_agent = Agent(
        name="privilege-escalation-explorer-agent",
        model="gpt-5.1",
        instructions=PRIVILEGE_ESCALATION_EXPLORER_PROMPT,
        output_type=PrivilegeEscalationExplorerOutput,
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

    return privilege_escalation_explorer_agent


async def run_privilege_escalation_exploration(
    application_capabilities: ApplicationCapabilityAnalysis,
    objective: str | None = None,
) -> PrivilegeEscalationExplorerOutput:
    """
    Run the privilege escalation exploration workflow.

    This function discovers all plausible privilege escalation vectors for an application
    by systematically evaluating MITRE ATT&CK Privilege Escalation techniques against
    the application's documented capabilities.

    Args:
        application_capabilities: Complete application capability analysis
        objective: Optional specific attacker objective that may inform which
                   privilege escalation methods are most relevant

    Returns:
        PrivilegeEscalationExplorerOutput with all discovered privilege escalation vectors
    """
    # Create the privilege escalation explorer agent
    privilege_escalation_explorer_agent = create_privilege_escalation_explorer_agent(
        application_capabilities
    )

    # Prepare input
    input_data = PrivilegeEscalationExplorerInput(
        application_capabilities=application_capabilities,
        objective=objective,
    )

    # Run the agent
    print("Running privilege escalation exploration...")
    result = await Runner.run(
        privilege_escalation_explorer_agent,
        input_data.model_dump_json(),
        max_turns=200,
    )

    return result.final_output

