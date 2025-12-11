from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

PRIVILEGE_ESCALATION_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Privilege Escalation",
    tactic_description="gain elevated permissions or access rights within the application",
    tactic_shortname="privilege-escalation",
    requires_prerequisite=False,
    search_objectives=[
        "permission escalation",
        "role modification",
        "admin access",
        "privilege upgrade",
        "access control bypass",
        "role assignment",
        "permission grant",
    ],
    focus_guidance="""   - What permission or role management mechanisms exist?
     - What access control features can be bypassed or abused?
     - What role assignment or privilege modification capabilities exist?
     - What admin or elevated access interfaces are available?""",
)
