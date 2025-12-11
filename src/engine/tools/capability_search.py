from agents import function_tool

from engine.models.app_breakdown import ApplicationCapabilityAnalysis


def get_application_capabilities_tool(
    application_capabilities: ApplicationCapabilityAnalysis,  # noqa: F821
):
    """Create a tool function that provides access to application capabilities.

    This factory function creates a tool that the agent can call to query
    the application capabilities as needed, rather than having it passed
    directly as input.

    Args:
        application_capabilities: The full application capability analysis
    """

    @function_tool
    async def get_application_capabilities(objective: str | None = None) -> str:
        """Get the application capabilities from the application capability analysis.

        Always returns the full application capabilities. The objective parameter is
        accepted for API compatibility but does not affect the returned data.

        Args:
            objective: Optional objective (accepted but not used for filtering).

        Returns:
            JSON string of full application capabilities.
        """
        return application_capabilities.model_dump_json()

    return get_application_capabilities
