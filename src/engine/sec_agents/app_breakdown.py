from agents import Agent, ModelSettings, Runner
from agents.tool import WebSearchTool
from openai.types.shared import Reasoning

from engine.models.app_breakdown import AppBreakdownInput, ApplicationCapabilityAnalysis
from engine.prompts.app_breakdown import APP_BREAKDOWN_PROMPT
from engine.tools.crawling import (
    fetch_sitemap_urls_from_robots_txt,
    fetch_urls_at_heirarchy_level_from_sitemap,
    get_page_content_as_markdown,
    list_links_on_page,
)

APP_BREAKDOWN_AGENT = Agent(
    name="app-breakdown-agent",
    model="gpt-5.1",
    instructions=APP_BREAKDOWN_PROMPT,
    output_type=ApplicationCapabilityAnalysis,
    model_settings=ModelSettings(
        reasoning=Reasoning(
            effort="high",
            summary="detailed",
        ),
        tool_choice="required",
        parallel_tool_calls=True,
    ),
    tools=[
        WebSearchTool(),
        fetch_urls_at_heirarchy_level_from_sitemap,
        list_links_on_page,
        get_page_content_as_markdown,
    ],
)


async def run_app_breakdown(
    app_urls: list[str], relevant_sitemap_urls: list[str] | None = None
) -> ApplicationCapabilityAnalysis:

    sitemap_urls: list[str] = []
    if relevant_sitemap_urls is None:
        for url in app_urls:
            sitemap_urls.extend(await fetch_sitemap_urls_from_robots_txt(url))
    else:
        sitemap_urls = relevant_sitemap_urls

    result = await Runner.run(
        APP_BREAKDOWN_AGENT,
        AppBreakdownInput(urls=app_urls, site_map_urls=sitemap_urls).model_dump_json(),
        max_turns=200,
    )
    return result.final_output
