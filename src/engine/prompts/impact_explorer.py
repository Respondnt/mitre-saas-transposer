from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

IMPACT_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Impact",
    tactic_description="manipulate, interrupt, or destroy systems and data",
    tactic_shortname="impact",
    requires_prerequisite=False,
    search_objectives=[
        "data deletion",
        "service disruption",
        "resource destruction",
        "account termination",
        "system manipulation",
        "data modification",
        "availability impact",
    ],
    focus_guidance="""   - What data or resource destruction mechanisms exist?
     - What service disruption or availability impact capabilities are available?
     - What system manipulation or modification features exist?
     - What account or resource termination capabilities can be abused?""",
)
