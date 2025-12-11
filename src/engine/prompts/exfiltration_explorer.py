from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

EXFILTRATION_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Exfiltration",
    tactic_description="steal and transfer data from the application to an external location",
    tactic_shortname="exfiltration",
    requires_prerequisite=False,
    search_objectives=[
        "data export",
        "file transfer",
        "data transmission",
        "external data sharing",
        "bulk data access",
        "data download",
        "information exfiltration",
    ],
    focus_guidance="""   - What data export or transfer mechanisms exist?
     - What external sharing or transmission features are available?
     - What bulk data access or download capabilities exist?
     - What information exfiltration channels can be used?""",
)
