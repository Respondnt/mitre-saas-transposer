from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

DISCOVERY_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Discovery",
    tactic_description="discover information about the application, its environment, or its tenant boundaries",
    tactic_shortname="discovery",
    requires_prerequisite=False,
    search_objectives=[
        "account enumeration",
        "user directory listing",
        "system information endpoint",
        "network configuration discovery",
        "cloud resource enumeration",
        "API endpoint discovery",
        "information disclosure",
    ],
    focus_guidance="""   - What information disclosure mechanisms exist in the application?
     - What enumeration or listing endpoints are available?
     - What user or account discovery features exist?
     - What system or environment information can be accessed?
     - What network or infrastructure discovery capabilities are available?""",
)
