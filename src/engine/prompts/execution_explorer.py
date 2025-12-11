from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

EXECUTION_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Execution",
    tactic_description="execute code, commands, or scripts within the application environment",
    tactic_shortname="execution",
    requires_prerequisite=False,
    search_objectives=[
        "code execution",
        "command execution",
        "script execution",
        "API endpoint execution",
        "workflow execution",
        "automation execution",
        "webhook execution",
    ],
    focus_guidance="""   - What execution mechanisms exist in the application?
     - What APIs or interfaces allow code/command execution?
     - What automation or workflow features can be leveraged?
     - What scripting or automation capabilities are available?""",
)
