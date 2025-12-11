from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

PERSISTENCE_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Persistence",
    tactic_description="maintain long-term access to the application or environment",
    tactic_shortname="persistence",
    requires_prerequisite=False,
    search_objectives=[
        "account creation",
        "token generation",
        "webhook registration",
        "integration setup",
        "scheduled task",
        "automation rule",
        "backup account",
    ],
    focus_guidance="""   - What mechanisms exist for maintaining access?
     - What account or credential management features are available?
     - What integration or webhook capabilities can be abused?
     - What automation or scheduling features exist?""",
)
