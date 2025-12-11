import os
import tempfile

import requests
from agents import function_tool
from mitreattack.stix20 import MitreAttackData

from engine.models.attack_paths import MitreTechnique

# Download MITRE ATT&CK data to a temporary folder
MITRE_DATA_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
_temp_dir = tempfile.mkdtemp(prefix="mitre_attack_")
_mitre_file_path = os.path.join(_temp_dir, "enterprise-attack.json")

# Download the file if it doesn't exist
if not os.path.exists(_mitre_file_path):
    response = requests.get(MITRE_DATA_URL, timeout=30)
    response.raise_for_status()
    with open(_mitre_file_path, "wb") as f:
        f.write(response.content)

MITRE_DATA_CACHE = MitreAttackData(stix_filepath=_mitre_file_path)


@function_tool
def get_all_mitre_tactics() -> list[str]:
    """List all shortname tactics from the MITRE ATT&CK STIX data.

    Returns:
        list[str]: A list of shortname tactics.
    """
    return [tactic.get_shortname() for tactic in MITRE_DATA_CACHE.get_tactics()]


@function_tool
def list_all_mitre_techniques_by_tactic_for_saas(
    tactic_name_shortname: str,
) -> list[dict]:
    """List all techniques by tactic for SaaS.

    Args:
        tactic_name_shortname: The name of the tactic to list techniques for.

    Returns:
        list[dict]: A list of technique dictionaries with name, description, and stix_id.
    """
    tactics = MITRE_DATA_CACHE.get_techniques_by_platform("SaaS")
    relevant_tactics = [
        tactic
        for tactic in tactics
        if any(
            phase.phase_name == tactic_name_shortname
            for phase in tactic.kill_chain_phases
        )
    ]
    return [
        MitreTechnique(
            name=tactic.name, description=tactic.description, stix_id=tactic.id
        ).model_dump()
        for tactic in relevant_tactics
    ]


@function_tool
def get_examples_of_technique_for_saas_from_mitre(
    stix_id: str,
) -> list[str]:
    """Get examples of a technique for SaaS from the MITRE ATT&CK STIX data.

    Args:
        stix_id: The STIX ID of the technique to get examples of.

    Returns:
        A list of 5 procedure examples for the technique.
    """
    return MITRE_DATA_CACHE.get_procedure_examples_by_technique(stix_id)[:5]
