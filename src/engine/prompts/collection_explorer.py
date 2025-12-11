from engine.prompts.tactic_explorer_template import generate_tactic_explorer_prompt

COLLECTION_EXPLORER_PROMPT = generate_tactic_explorer_prompt(
    tactic_name="Collection",
    tactic_description="gather and collect data of interest from the application",
    tactic_shortname="collection",
    requires_prerequisite=False,
    search_objectives=[
        "data export",
        "data retrieval",
        "file download",
        "information gathering",
        "data collection",
        "content access",
        "resource enumeration",
    ],
    focus_guidance="""   - What data collection or export mechanisms exist?
     - What information retrieval or access features are available?
     - What file download or content access capabilities exist?
     - What data enumeration or discovery features can be used?""",
)
