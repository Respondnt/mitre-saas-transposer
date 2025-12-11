from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

LATERAL_MOVEMENT_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Lateral Movement",
    tactic_description="move through the application environment to access additional resources or systems",
    tactic_shortname="lateral-movement",
    requires_prerequisite=False,
    search_objectives=[
        "cross-tenant access",
        "workspace switching",
        "resource access",
        "system navigation",
        "environment traversal",
        "multi-system access",
        "cross-boundary access",
    ],
    focus_guidance="""   - What mechanisms exist for moving between resources or systems?
     - What cross-tenant or cross-workspace access capabilities exist?
     - What resource navigation or traversal features are available?
     - What multi-system or multi-environment access mechanisms exist?""",
)
