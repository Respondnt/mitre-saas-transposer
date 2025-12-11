from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

INITIAL_ACCESS_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Initial Access",
    tactic_description="gain entry to the application, its environment, or its tenant boundaries",
    tactic_shortname="initial-access",
    requires_prerequisite=False,
    search_objectives=[
        "public registration",
        "OAuth integration",
        "exposed API keys",
        "webhook endpoint",
        "supply chain integration",
        "authentication bypass",
        "credential access",
    ],
    focus_guidance="""   - What are the application's authentication mechanisms?
     - What public-facing interfaces exist?
     - What registration or onboarding flows are available?
     - What integration or API entry points are exposed?
     - What external services or dependencies could be entry vectors?""",
)
