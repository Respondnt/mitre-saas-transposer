from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

COMMAND_AND_CONTROL_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Command and Control",
    tactic_description="establish and maintain communication channels with external systems",
    tactic_shortname="command-and-control",
    requires_prerequisite=False,
    search_objectives=[
        "outbound communication",
        "webhook endpoint",
        "API callback",
        "external integration",
        "network communication",
        "external service connection",
        "communication channel",
    ],
    focus_guidance="""   - What outbound communication mechanisms exist?
     - What webhook or callback capabilities are available?
     - What external integration or service connection features exist?
     - What network communication channels can be established?""",
)
