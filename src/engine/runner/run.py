import asyncio
import os

from pydantic import BaseModel

from engine.models.attack_paths import (
    CollectionExplorerOutput,
    CommandAndControlExplorerOutput,
    CredentialAccessExplorerOutput,
    DefenseEvasionExplorerOutput,
    DiscoveryExplorerOutput,
    ExecutionExplorerOutput,
    ExfiltrationExplorerOutput,
    ImpactExplorerOutput,
    InitialAccessExplorerOutput,
    LateralMovementExplorerOutput,
    PersistenceExplorerOutput,
    PrivilegeEscalationExplorerOutput,
)
from engine.sec_agents.app_breakdown import run_app_breakdown
from engine.sec_agents.collection_explorer import run_collection_exploration
from engine.sec_agents.command_and_control_explorer import (
    run_command_and_control_exploration,
)
from engine.sec_agents.credential_access_explorer import (
    run_credential_access_exploration,
)
from engine.sec_agents.defense_evasion_explorer import run_defense_evasion_exploration
from engine.sec_agents.discovery_explorer import run_discovery_exploration
from engine.sec_agents.execution_explorer import run_execution_exploration
from engine.sec_agents.exfiltration_explorer import run_exfiltration_exploration
from engine.sec_agents.impact_explorer import run_impact_exploration
from engine.sec_agents.initial_access_explorer import run_initial_access_exploration
from engine.sec_agents.lateral_movement_explorer import run_lateral_movement_exploration
from engine.sec_agents.persistence_explorer import run_persistence_exploration
from engine.sec_agents.privilege_escalation_explorer import (
    run_privilege_escalation_exploration,
)


class ComprehensiveAnalysisResults(BaseModel):
    """Comprehensive results from running all tactic explorer agents."""

    application_name: str
    initial_access: InitialAccessExplorerOutput
    discovery: DiscoveryExplorerOutput
    execution: ExecutionExplorerOutput
    persistence: PersistenceExplorerOutput
    privilege_escalation: PrivilegeEscalationExplorerOutput
    defense_evasion: DefenseEvasionExplorerOutput
    credential_access: CredentialAccessExplorerOutput
    lateral_movement: LateralMovementExplorerOutput
    collection: CollectionExplorerOutput
    command_and_control: CommandAndControlExplorerOutput
    exfiltration: ExfiltrationExplorerOutput
    impact: ImpactExplorerOutput


async def run_analysis(objective: str | None = None):
    if os.getenv("OPENAI_API_KEY") is None:
        raise ValueError("OPENAI_API_KEY is not set")

    app_breakdown = await run_app_breakdown(
        [
            "https://github.com/",
            "https://docs.github.com/en",
            "https://docs.github.com/en/rest",
        ],
        relevant_sitemap_urls=[],
    )
    (
        initial_access_result,
        discovery_result,
        execution_result,
        persistence_result,
        privilege_escalation_result,
        defense_evasion_result,
        credential_access_result,
        lateral_movement_result,
        collection_result,
        command_and_control_result,
        exfiltration_result,
        impact_result,
    ) = await asyncio.gather(
        run_initial_access_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_discovery_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_execution_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_persistence_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_privilege_escalation_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_defense_evasion_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_credential_access_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_lateral_movement_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_collection_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_command_and_control_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_exfiltration_exploration(
            app_breakdown,
            objective=objective,
        ),
        run_impact_exploration(
            app_breakdown,
            objective=objective,
        ),
    )
    return ComprehensiveAnalysisResults(
        application_name=app_breakdown.application_name,
        initial_access=initial_access_result,
        discovery=discovery_result,
        execution=execution_result,
        persistence=persistence_result,
        privilege_escalation=privilege_escalation_result,
        defense_evasion=defense_evasion_result,
        credential_access=credential_access_result,
        lateral_movement=lateral_movement_result,
        collection=collection_result,
        command_and_control=command_and_control_result,
        exfiltration=exfiltration_result,
        impact=impact_result,
    )
