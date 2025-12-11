from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

DEFENSE_EVASION_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Defense Evasion",
    tactic_description="avoid detection or bypass security controls",
    tactic_shortname="defense-evasion",
    requires_prerequisite=False,
    search_objectives=[
        "audit log bypass",
        "logging evasion",
        "monitoring bypass",
        "detection evasion",
        "security control bypass",
        "anomaly avoidance",
        "legitimate activity mimicry",
    ],
    focus_guidance="""   - What security controls or monitoring mechanisms exist?
     - What audit logging or detection features can be evaded?
     - What legitimate activity patterns can be mimicked?
     - What security control bypass mechanisms are available?""",
)
