from agents import Agent, ModelSettings, Runner
from agents.model_settings import Reasoning

from engine.models.app_breakdown import ApplicationCapabilityAnalysis
from engine.models.attack_paths import (
    CommandAndControlExplorerInput,
    CommandAndControlExplorerOutput,
)
from engine.prompts.command_and_control_explorer import (
    COMMAND_AND_CONTROL_EXPLORER_PROMPT,
)
from engine.sec_agents.capability_search import create_capability_search_agent
from engine.tools.crawling import get_page_content_as_markdown, list_links_on_page
from engine.tools.environment_search import get_environment_constraints_tool
from engine.tools.mitre_attack import (
    get_all_mitre_tactics,
    get_examples_of_technique_for_saas_from_mitre,
    list_all_mitre_techniques_by_tactic_for_saas,
)


def create_command_and_control_explorer_agent(
    application_capabilities: ApplicationCapabilityAnalysis,
):
    """Create a command and control explorer agent that discovers all command and control vectors.

    This factory function creates an agent that can systematically discover all
    plausible command and control methods an attacker could use.

    Args:
        application_capabilities: The full application capability analysis
    """
    # Create the capability search agent as a tool
    capability_search_tool = create_capability_search_agent(application_capabilities)

    # Create the Command and Control Explorer Agent
    command_and_control_explorer_agent = Agent(
        name="command-and-control-explorer-agent",
        model="gpt-5.1",
        instructions=COMMAND_AND_CONTROL_EXPLORER_PROMPT,
        output_type=CommandAndControlExplorerOutput,
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

    return command_and_control_explorer_agent


async def run_command_and_control_exploration(
    application_capabilities: ApplicationCapabilityAnalysis,
    objective: str | None = None,
) -> CommandAndControlExplorerOutput:
    """
    Run the command and control exploration workflow.

    This function discovers all plausible command and control vectors for an application
    by systematically evaluating MITRE ATT&CK Command and Control techniques against
    the application's documented capabilities.

    Args:
        application_capabilities: Complete application capability analysis
        objective: Optional specific attacker objective that may inform which
                   command and control methods are most relevant

    Returns:
        CommandAndControlExplorerOutput with all discovered command and control vectors
    """
    # Create the command and control explorer agent
    command_and_control_explorer_agent = create_command_and_control_explorer_agent(
        application_capabilities
    )

    # Prepare input
    input_data = CommandAndControlExplorerInput(
        application_capabilities=application_capabilities,
        objective=objective,
    )

    # Run the agent
    print("Running command and control exploration...")
    result = await Runner.run(
        command_and_control_explorer_agent,
        input_data.model_dump_json(),
        max_turns=200,
    )

    return result.final_output



