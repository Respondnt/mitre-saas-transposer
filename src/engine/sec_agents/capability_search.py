from agents import Agent, ModelSettings
from openai.types.shared import Reasoning

from engine.models.app_breakdown import ApplicationCapabilityAnalysis
from engine.models.attack_paths import CapabilitySearchOutput
from engine.prompts.capability_search import CAPABILITY_SEARCH_AGENT_PROMPT
from engine.tools.capability_search import get_application_capabilities_tool


def create_capability_search_agent(
    application_capabilities: ApplicationCapabilityAnalysis,
):
    """Create a capability search agent that intelligently searches application capabilities.

    This factory function creates an agent that can search through the application
    capabilities using reasoning to find relevant features, interfaces, and data
    that could be used to achieve specific attack objectives.

    Args:
        application_capabilities: The full application capability analysis
    """
    # Create the capability search agent
    capability_search_agent = Agent(
        name="capability-search-agent",
        model="gpt-5.1",
        instructions=CAPABILITY_SEARCH_AGENT_PROMPT,
        output_type=CapabilitySearchOutput,
        model_settings=ModelSettings(
            reasoning=Reasoning(
                effort="high",
                summary="detailed",
            ),
            parallel_tool_calls=False,
        ),
        tools=[get_application_capabilities_tool(application_capabilities)],
    )

    # Return the agent configured as a tool with the application capabilities in context
    return capability_search_agent.as_tool(
        tool_name="search_application_capabilities",
        tool_description=(
            "Search the application capabilities to find means to achieve a specific objective. "
            "Use this to understand what capabilities, interfaces, and data the application provides "
            "that could help achieve a specific MITRE tactic or attack objective. You can call this "
            "multiple times with different objectives to explore different attack paths. "
            "Results are automatically cached for efficiency. "
            "Input: objective (string describing what you're trying to achieve). "
            "Output: CapabilitySearchOutput with relevant capabilities, interfaces, data, permissions, "
            "attack surface summary, and applicable MITRE techniques."
        ),
    )
