from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

CREDENTIAL_ACCESS_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Credential Access",
    tactic_description="steal credentials, tokens, or authentication information",
    tactic_shortname="credential-access",
    requires_prerequisite=False,
    search_objectives=[
        "credential storage",
        "token access",
        "password retrieval",
        "API key access",
        "authentication token",
        "credential export",
        "session token",
    ],
    focus_guidance="""   - What credential or token storage mechanisms exist?
     - What authentication information can be accessed or exported?
     - What API key or token management features are available?
     - What credential disclosure vulnerabilities exist?""",
)
