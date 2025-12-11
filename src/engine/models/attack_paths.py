from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from engine.models.app_breakdown import ApplicationCapabilityAnalysis


class HypothesisStep(BaseModel):
    """A step in an attack hypothesis."""

    model_config = ConfigDict(extra="forbid")

    step_name: str = Field(description="The name of the step")
    step_description: str = Field(description="A description of the step")
    step_mitre_technique: str = Field(
        description="The MITRE ATT&CK technique that this step is associated with"
    )
    step_mitre_tactic: str = Field(
        description="The MITRE ATT&CK tactic that this step is associated with"
    )


class AttackHypothesis(BaseModel):
    """A realistic attack scenario based on MITRE tactics."""

    model_config = ConfigDict(extra="forbid")

    scenario_name: str = Field(
        description="Short, descriptive name for this attack scenario"
    )
    attack_target: str = Field(
        description="If the attack is successfully achieved, what will the adversary achieve?"
    )
    starting_tactic: str = Field(
        description="The MITRE tactic representing the initial access or starting point"
    )
    objective_tactic: str = Field(
        description="The MITRE tactic representing the ultimate goal"
    )
    preconditions: str = Field(
        description="What the attacker needs to have or know to start"
    )
    attack_flow_hypothesis: list[HypothesisStep] = Field(
        description="The hypothesised steps in the attack scenario that lead from the starting tactic to the objective tactic"
    )


class HypothesisGeneratorOutput(BaseModel):
    """Output from the hypothesis generation agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    hypotheses: list[AttackHypothesis] = Field(
        description="List of realistic attack scenarios generated"
    )
    tactics_covered: list[str] = Field(
        description="List of MITRE tactics covered across all hypotheses"
    )
    rationale: str = Field(
        description="Brief explanation of why these scenarios were chosen"
    )


class MethodStep(BaseModel):
    """
    A single discrete attacker action taken to achieve the tactic.
    Steps must be sequential, realistic, and grounded in the application's capabilities.
    """

    step_id: int = Field(..., description="Sequential step number (starting from 1).")

    description: str = Field(
        ...,
        description=(
            "A clear, concise description of the attacker action performed in this step, "
            "adapted to the scenario, selected MITRE technique(s), and application's capabilities."
        ),
    )

    related_capabilities: list[str] = Field(
        default_factory=list,
        description=(
            "List of specific capabilities from the ApplicationCapabilityAnalysis that enable this step "
            "(e.g., data export feature, messaging API, integration management interface)."
        ),
    )

    related_interfaces: list[str] = Field(
        default_factory=list,
        description=(
            "Specific UI flows, API endpoints, integration points, or other interfaces used during this step. "
            "These must exist in the ApplicationCapabilityAnalysis."
        ),
    )

    related_data: list[str] = Field(
        default_factory=list,
        description=(
            "Data types or specific data assets accessed, modified, or exfiltrated in this step "
            "(e.g., user profiles, workspace messages, audit logs)."
        ),
    )

    notes: Optional[str] = Field(
        None,
        description=(
            "Optional contextual notes about the step, such as constraints, reasoning, attacker intent, "
            "or mapping to MITRE procedure examples."
        ),
    )


class SelectedTechnique(BaseModel):
    """
    A MITRE technique selected as relevant for achieving this tactic.
    Includes rationale to help the orchestrator understand the reasoning.
    """

    stix_id: str = Field(
        ..., description="The MITRE ATT&CK STIX ID for the technique (e.g., T1078)."
    )

    name: str = Field(
        ...,
        description="The human-readable name of the MITRE technique (e.g., Valid Accounts).",
    )

    rationale: str = Field(
        ...,
        description=(
            "Explanation of why this technique is relevant and realistic for the given scenario, "
            "tactic, preconditions, and application capabilities."
        ),
    )


class AdversarialMethod(BaseModel):
    """
    Structured output describing whether and how the attacker can achieve the specified MITRE tactic.
    This object is consumed by the orchestrator to assemble multi-tactic attack paths.
    """

    can_achieve: bool = Field(
        ...,
        description=(
            "Indicates whether the given tactic can realistically be achieved using the application's "
            "documented capabilities and the scenario's preconditions. If false, all other fields "
            "(except comments_for_orchestrator) may be empty."
        ),
    )

    tactic_name: str = Field(
        ...,
        description="The MITRE ATT&CK tactic being addressed (e.g., Persistence, Collection, Exfiltration).",
    )

    selected_techniques: list[SelectedTechnique] = Field(
        default_factory=list,
        description=(
            "One or two MITRE techniques chosen as the most realistic for achieving this tactic given "
            "the scenario context and application capabilities."
        ),
    )

    method_steps: list[MethodStep] = Field(
        default_factory=list,
        description=(
            "A sequential list of realistic attacker actions the adversary would take to achieve the tactic. "
            "Each action must be grounded in the application's capabilities and informed by MITRE procedure examples."
        ),
    )

    capabilities_used: list[str] = Field(
        default_factory=list,
        description=(
            "List of all capabilities from the ApplicationCapabilityAnalysis that enable this tactic—"
            "aggregated across all steps."
        ),
    )

    interfaces_used: list[str] = Field(
        default_factory=list,
        description=(
            "All specific interfaces (endpoints, UI flows, integration points) used to perform this tactic—"
            "aggregated across all steps."
        ),
    )

    data_accessed: list[str] = Field(
        default_factory=list,
        description=(
            "All data assets accessed, modified, or exfiltrated across the tactic's method execution."
        ),
    )

    preconditions_required: list[str] = Field(
        default_factory=list,
        description=(
            "Additional preconditions (beyond those provided at input) that must hold for this method to succeed—"
            "e.g., attacker must already control a compromised user, must have an OAuth token, "
            "must access a specific workspace."
        ),
    )

    constraints_encountered: list[str] = Field(
        default_factory=list,
        description=(
            "Limitations imposed by permissions, RBAC, audit logging, rate limits, or capability restrictions "
            "that the attacker must work around or that may affect feasibility."
        ),
    )

    evasion_considerations: list[str] = Field(
        default_factory=list,
        description=(
            "List of realistic detection-evasion strategies the attacker might employ in this step chain—"
            "e.g., low-and-slow access, mimicking legitimate user activity, using official APIs."
        ),
    )

    comments_for_orchestrator: Optional[str] = Field(
        None,
        description=(
            "Optional notes intended for the orchestrator agent. May include suggestions for chaining, warnings "
            "about feasibility, or context useful for subsequent tactics."
        ),
    )


class AdversarialMethodOutput(BaseModel):
    """Output from the adversarial agent."""

    model_config = ConfigDict(extra="forbid")

    scenario_name: str = Field(description="Name of the scenario being analyzed")
    methods: list[AdversarialMethod] = Field(
        description="Methods for achieving each tactic in the attack chain"
    )


class AttackPath(BaseModel):
    """Complete attack path including hypothesis, methods, and detection."""

    model_config = ConfigDict(extra="forbid")

    scenario_name: str = Field(description="Name of the attack scenario")
    hypothesis: AttackHypothesis = Field(description="The original attack hypothesis")
    adversarial_methods: list[AdversarialMethod] = Field(
        description="Methods for achieving each tactic"
    )
    attack_chain_summary_steps: list[str] = Field(
        description="Step-by-step summary of the complete attack path"
    )


class AttackPathOutput(BaseModel):
    """Complete output of the attack path generation workflow."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application")
    attack_paths: list[AttackPath] = Field(
        description="All generated attack paths with methods and detections"
    )
    summary: str = Field(
        description="Executive summary of findings and recommendations"
    )


class AttackPathGenerationInput(BaseModel):
    """Input for the attack path generation workflow."""

    application_capabilities: ApplicationCapabilityAnalysis


class AdversarialAgentInput(BaseModel):
    """Input for the adversarial agent when invoked as a tool."""

    scenario_description: str = Field(description="The overall attack scenario context")
    tactic_to_achieve: str = Field(
        description="The specific MITRE ATT&CK tactic to achieve (e.g., 'Persistence', 'Collection')"
    )
    preconditions: str = Field(
        description="What the attacker has/knows at this point in the attack chain"
    )


class CapabilitySearchInput(BaseModel):
    """Input for the capability search agent."""

    objective: str = Field(
        description="A description of what you're trying to achieve (e.g., 'exfiltrate data', 'establish persistence', 'escalate privileges', 'access sensitive information')"
    )


class CapabilitySearchOutput(BaseModel):
    """Output from the capability search agent."""

    model_config = ConfigDict(extra="forbid")

    objective: str = Field(description="The objective that was searched for")
    is_achievable: bool = Field(
        description="Whether the objective is achievable given the application's capabilities"
    )
    explanation: str = Field(
        description="A short 2-3 sentence explanation of why the objective is achievable or not"
    )
    relevant_capabilities: list[str] = Field(
        description="Specific capabilities that could enable this objective, with brief explanations"
    )
    relevant_interfaces: list[str] = Field(
        description="Specific interfaces (API endpoints, UI features, etc.) that could be leveraged"
    )
    evidence_reference: list[str] = Field(
        description="References to the evidence that supports the capability search"
    )
    relevant_data: list[str] = Field(
        description="Specific data types or resources that could be accessed or manipulated"
    )
    relevant_permissions: list[str] = Field(
        description="Permissions or access controls relevant to this objective"
    )
    attack_surface_summary: str = Field(
        description="Brief summary of how these capabilities could be combined to achieve the objective"
    )
    mitre_techniques: list[str] = Field(
        description="Specific MITRE ATT&CK techniques that could be applied given these capabilities"
    )


class InitialAccessVector(BaseModel):
    """
    A single initial access vector describing how an attacker could gain entry to the application.
    Similar to AdversarialMethod but focused exclusively on Initial Access.
    """

    can_achieve: bool = Field(
        ...,
        description=(
            "Indicates whether this initial access vector can realistically be achieved using the application's "
            "documented capabilities. If false, all other fields (except comments) may be empty."
        ),
    )

    technique_name: str = Field(
        ...,
        description="The MITRE ATT&CK Initial Access technique name (e.g., Valid Accounts, Exploit Public-Facing Application).",
    )

    technique_stix_id: str = Field(
        ...,
        description="The MITRE ATT&CK STIX ID for the technique (e.g., T1078, T1190).",
    )

    method_steps: list[MethodStep] = Field(
        default_factory=list,
        description=(
            "A sequential list of realistic attacker actions to gain initial access. "
            "Each action must be grounded in the application's capabilities and informed by MITRE procedure examples."
        ),
    )

    capabilities_used: list[str] = Field(
        default_factory=list,
        description=(
            "List of all capabilities from the ApplicationCapabilityAnalysis that enable this initial access vector."
        ),
    )

    interfaces_used: list[str] = Field(
        default_factory=list,
        description=(
            "All specific interfaces (endpoints, UI flows, integration points) used to gain initial access."
        ),
    )

    data_accessed: list[str] = Field(
        default_factory=list,
        description=(
            "Data assets accessed or obtained during initial access (e.g., credentials, tokens, user profiles)."
        ),
    )

    preconditions_required: list[str] = Field(
        default_factory=list,
        description=(
            "Preconditions that must hold for this initial access vector to succeed—"
            "e.g., attacker must have valid credentials, must have access to a specific domain, "
            "must be able to register an account."
        ),
    )

    constraints_encountered: list[str] = Field(
        default_factory=list,
        description=(
            "Limitations imposed by permissions, RBAC, authentication requirements, rate limits, "
            "or capability restrictions that the attacker must work around."
        ),
    )

    evasion_considerations: list[str] = Field(
        default_factory=list,
        description=(
            "Realistic detection-evasion strategies the attacker might employ—"
            "e.g., using legitimate registration flows, timing attacks, credential stuffing."
        ),
    )

    resulting_access: str = Field(
        ...,
        description=(
            "Description of what access the attacker gains after successfully executing this initial access vector—"
            "e.g., 'Authenticated user account with basic permissions', 'API token with read access', "
            "'OAuth token for workspace access'."
        ),
    )

    comments: Optional[str] = Field(
        None,
        description=(
            "Optional notes about this initial access vector, such as likelihood, commonality, "
            "or context useful for understanding its role in attack paths."
        ),
    )


class InitialAccessExplorerOutput(BaseModel):
    """Output from the initial access explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[InitialAccessVector] = Field(
        description="All discovered initial access vectors for the application"
    )
    summary: str = Field(
        description="Summary of initial access findings and overall attack surface entry points"
    )


class InitialAccessExplorerInput(BaseModel):
    """Input for the initial access explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which initial access vectors are most relevant",
    )


class DiscoveryVector(BaseModel):
    """
    A single discovery vector describing how an attacker could discover information about the application
    after gaining initial access. Similar to InitialAccessVector but focused exclusively on Discovery.
    """

    can_achieve: bool = Field(
        ...,
        description=(
            "Indicates whether this discovery vector can realistically be achieved using the application's "
            "documented capabilities and the attacker's current access level. If false, all other fields (except comments) may be empty."
        ),
    )

    technique_name: str = Field(
        ...,
        description="The MITRE ATT&CK Discovery technique name (e.g., Account Discovery, System Information Discovery).",
    )

    technique_stix_id: str = Field(
        ...,
        description="The MITRE ATT&CK STIX ID for the technique (e.g., T1087, T1082).",
    )

    method_steps: list[MethodStep] = Field(
        default_factory=list,
        description=(
            "A sequential list of realistic attacker actions to discover information. "
            "Each action must be grounded in the application's capabilities and informed by MITRE procedure examples. "
            "The first step should reference the attacker's current access from the initial access vector."
        ),
    )

    capabilities_used: list[str] = Field(
        default_factory=list,
        description=(
            "List of all capabilities from the ApplicationCapabilityAnalysis that enable this discovery vector."
        ),
    )

    interfaces_used: list[str] = Field(
        default_factory=list,
        description=(
            "All specific interfaces (endpoints, UI flows, integration points) used to perform discovery."
        ),
    )

    data_accessed: list[str] = Field(
        default_factory=list,
        description=(
            "Data assets accessed or discovered during discovery (e.g., user lists, system information, network configuration)."
        ),
    )

    preconditions_required: list[str] = Field(
        default_factory=list,
        description=(
            "Additional preconditions (beyond the initial access vector) that must hold for this discovery vector to succeed—"
            "e.g., attacker must have access to specific endpoints, must have certain permissions, "
            "must be able to enumerate users."
        ),
    )

    constraints_encountered: list[str] = Field(
        default_factory=list,
        description=(
            "Limitations imposed by permissions, RBAC, access controls, rate limits, "
            "or capability restrictions that the attacker must work around."
        ),
    )

    evasion_considerations: list[str] = Field(
        default_factory=list,
        description=(
            "Realistic detection-evasion strategies the attacker might employ—"
            "e.g., using legitimate API calls, timing attacks, low-and-slow enumeration."
        ),
    )

    information_discovered: str = Field(
        ...,
        description=(
            "Description of what information the attacker discovers after successfully executing this discovery vector—"
            "e.g., 'List of all user accounts in the workspace', 'System configuration and version information', "
            "'Network topology and connected services'."
        ),
    )

    comments: Optional[str] = Field(
        None,
        description=(
            "Optional notes about this discovery vector, such as likelihood, commonality, "
            "or context useful for understanding its role in attack paths."
        ),
    )


class DiscoveryExplorerInput(BaseModel):
    """Input for the discovery explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which discovery methods are most relevant",
    )


class DiscoveryExplorerOutput(BaseModel):
    """Output from the discovery explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[DiscoveryVector] = Field(
        description="All discovered discovery vectors for the application from the given initial access vector"
    )
    summary: str = Field(
        description="Summary of discovery findings and information that can be gathered from the initial access position"
    )


class EnvironmentConstraint(BaseModel):
    """An environment constraint that may affect initial access vectors."""

    name: str = Field(description="Name of the constraint")
    description: str = Field(description="Detailed description of the constraint")
    relevance: str = Field(
        description="Description of when and how this constraint is relevant to initial access exploration"
    )


class MitreTactic(BaseModel):
    name: str
    description: str


class MitreTechnique(BaseModel):
    stix_id: str
    name: str
    description: str


class SecurityControl(BaseModel):
    """
    A security control or mitigation that could make an attack vector harder to execute.
    """

    control_name: str = Field(
        ...,
        description="Name of the security control or mitigation (e.g., 'Multi-Factor Authentication', 'Rate Limiting', 'IP Allowlisting').",
    )

    control_type: str = Field(
        ...,
        description="Type of control (e.g., 'Authentication', 'Authorization', 'Network Security', 'Monitoring', 'Input Validation').",
    )

    description: str = Field(
        ...,
        description="Detailed description of how this control works and what it protects against.",
    )

    is_implemented: bool = Field(
        ...,
        description="Whether this control is actually implemented in the application based on the documentation analysis.",
    )

    implementation_details: str = Field(
        ...,
        description="Specific details about how the control is implemented, including configuration options, requirements, and how it works.",
    )

    evidence_references: list[str] = Field(
        default_factory=list,
        description="URLs or references to documentation that provide evidence for this control's existence and implementation.",
    )

    effectiveness_against_attack: str = Field(
        ...,
        description="Assessment of how effective this control is against the specific attack vector being analyzed. Explain whether it would prevent, significantly hinder, or have minimal impact on the attack.",
    )

    bypass_possibilities: list[str] = Field(
        default_factory=list,
        description="Potential ways an attacker might bypass or work around this control, if any.",
    )

    configuration_requirements: list[str] = Field(
        default_factory=list,
        description="Configuration requirements or settings needed for this control to be effective (e.g., 'MFA must be enabled for all users', 'IP allowlist must be configured').",
    )


class SecurityControlAnalysis(BaseModel):
    """
    Analysis of security controls for a specific attack vector.
    """

    attack_vector_technique: str = Field(
        ...,
        description="The MITRE ATT&CK technique name associated with the attack vector being analyzed.",
    )

    attack_vector_stix_id: str = Field(
        ...,
        description="The MITRE ATT&CK STIX ID for the technique.",
    )

    attack_vector_summary: str = Field(
        ...,
        description="Brief summary of the attack vector being analyzed.",
    )

    security_controls: list[SecurityControl] = Field(
        default_factory=list,
        description="List of security controls or mitigations that could affect this attack vector.",
    )

    overall_mitigation_assessment: str = Field(
        ...,
        description="Overall assessment of how well the application is protected against this attack vector based on the identified controls.",
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for additional security controls or configuration improvements that could better protect against this attack vector.",
    )


class SecurityControlAnalyzerInput(BaseModel):
    """Input for the security control analyzer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    attack_vectors: list[
        Union[InitialAccessVector, DiscoveryVector, AdversarialMethod]
    ] = Field(
        ...,
        description="List of attack vectors to analyze for security controls and mitigations. Can include InitialAccessVector, DiscoveryVector, or AdversarialMethod.",
    )
    objective: Optional[str] = Field(
        default=None,
        description="Optional context or objective that may inform which security controls are most relevant",
    )


class SecurityControlAnalyzerOutput(BaseModel):
    """Output from the security control analyzer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    control_analyses: list[SecurityControlAnalysis] = Field(
        description="Security control analysis for each attack vector provided"
    )
    summary: str = Field(
        description="Summary of security control findings and overall protection posture"
    )


# Generic Tactic Vector - base structure for all tactic vectors
class TacticVector(BaseModel):
    """Base structure for tactic-specific attack vectors."""

    can_achieve: bool = Field(
        ...,
        description=(
            "Indicates whether this vector can realistically be achieved using the application's "
            "documented capabilities and the attacker's current access level. If false, all other fields (except comments) may be empty."
        ),
    )

    technique_name: str = Field(
        ...,
        description="The MITRE ATT&CK technique name for this tactic.",
    )

    technique_stix_id: str = Field(
        ...,
        description="The MITRE ATT&CK STIX ID for the technique.",
    )

    method_steps: list[MethodStep] = Field(
        default_factory=list,
        description=(
            "A sequential list of realistic attacker actions to achieve this tactic. "
            "Each action must be grounded in the application's capabilities and informed by MITRE procedure examples."
        ),
    )

    capabilities_used: list[str] = Field(
        default_factory=list,
        description=(
            "List of all capabilities from the ApplicationCapabilityAnalysis that enable this vector."
        ),
    )

    interfaces_used: list[str] = Field(
        default_factory=list,
        description=(
            "All specific interfaces (endpoints, UI flows, integration points) used to perform this tactic."
        ),
    )

    data_accessed: list[str] = Field(
        default_factory=list,
        description=(
            "Data assets accessed, modified, or used during this tactic execution."
        ),
    )

    preconditions_required: list[str] = Field(
        default_factory=list,
        description=(
            "Additional preconditions that must hold for this vector to succeed—"
            "e.g., attacker must have access to specific endpoints, must have certain permissions."
        ),
    )

    constraints_encountered: list[str] = Field(
        default_factory=list,
        description=(
            "Limitations imposed by permissions, RBAC, access controls, rate limits, "
            "or capability restrictions that the attacker must work around."
        ),
    )

    evasion_considerations: list[str] = Field(
        default_factory=list,
        description=(
            "Realistic detection-evasion strategies the attacker might employ."
        ),
    )

    comments: Optional[str] = Field(
        None,
        description=(
            "Optional notes about this vector, such as likelihood, commonality, "
            "or context useful for understanding its role in attack paths."
        ),
    )


# Execution Vector
class ExecutionVector(TacticVector):
    """A single execution vector describing how an attacker could execute code or commands."""

    execution_result: str = Field(
        ...,
        description=(
            "Description of what the attacker achieves after successfully executing this vector—"
            "e.g., 'Code execution in application environment', 'Command execution via API', "
            "'Script execution in automation workflow'."
        ),
    )


class ExecutionExplorerInput(BaseModel):
    """Input for the execution explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which execution methods are most relevant",
    )


class ExecutionExplorerOutput(BaseModel):
    """Output from the execution explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[ExecutionVector] = Field(
        description="All discovered execution vectors for the application"
    )
    summary: str = Field(
        description="Summary of execution findings and methods available from the starting position"
    )


# Persistence Vector
class PersistenceVector(TacticVector):
    """A single persistence vector describing how an attacker could maintain long-term access."""

    persistence_mechanism: str = Field(
        ...,
        description=(
            "Description of the persistence mechanism established—"
            "e.g., 'Backup account with admin privileges', 'Webhook endpoint registered', "
            "'Scheduled automation rule that maintains access'."
        ),
    )


class PersistenceExplorerInput(BaseModel):
    """Input for the persistence explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which persistence methods are most relevant",
    )


class PersistenceExplorerOutput(BaseModel):
    """Output from the persistence explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[PersistenceVector] = Field(
        description="All discovered persistence vectors for the application"
    )
    summary: str = Field(
        description="Summary of persistence findings and mechanisms available from the starting position"
    )


# Privilege Escalation Vector
class PrivilegeEscalationVector(TacticVector):
    """A single privilege escalation vector describing how an attacker could gain elevated permissions."""

    escalated_access: str = Field(
        ...,
        description=(
            "Description of the elevated access or permissions gained—"
            "e.g., 'Admin role assigned to attacker account', 'Elevated API token with write permissions', "
            "'Privileged access to sensitive resources'."
        ),
    )


class PrivilegeEscalationExplorerInput(BaseModel):
    """Input for the privilege escalation explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which privilege escalation methods are most relevant",
    )


class PrivilegeEscalationExplorerOutput(BaseModel):
    """Output from the privilege escalation explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[PrivilegeEscalationVector] = Field(
        description="All discovered privilege escalation vectors for the application"
    )
    summary: str = Field(
        description="Summary of privilege escalation findings and methods available from the starting position"
    )


# Defense Evasion Vector
class DefenseEvasionVector(TacticVector):
    """A single defense evasion vector describing how an attacker could avoid detection."""

    evasion_achieved: str = Field(
        ...,
        description=(
            "Description of what evasion is achieved—"
            "e.g., 'Audit logging bypassed', 'Security monitoring evaded', "
            "'Legitimate activity pattern established to avoid detection'."
        ),
    )


class DefenseEvasionExplorerInput(BaseModel):
    """Input for the defense evasion explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which defense evasion methods are most relevant",
    )


class DefenseEvasionExplorerOutput(BaseModel):
    """Output from the defense evasion explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[DefenseEvasionVector] = Field(
        description="All discovered defense evasion vectors for the application"
    )
    summary: str = Field(
        description="Summary of defense evasion findings and methods available from the starting position"
    )


# Credential Access Vector
class CredentialAccessVector(TacticVector):
    """A single credential access vector describing how an attacker could steal credentials or tokens."""

    credentials_obtained: str = Field(
        ...,
        description=(
            "Description of what credentials or authentication information is obtained—"
            "e.g., 'API keys extracted from configuration', 'OAuth tokens stolen from session', "
            "'Password hashes retrieved from database'."
        ),
    )


class CredentialAccessExplorerInput(BaseModel):
    """Input for the credential access explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which credential access methods are most relevant",
    )


class CredentialAccessExplorerOutput(BaseModel):
    """Output from the credential access explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[CredentialAccessVector] = Field(
        description="All discovered credential access vectors for the application"
    )
    summary: str = Field(
        description="Summary of credential access findings and methods available from the starting position"
    )


# Lateral Movement Vector
class LateralMovementVector(TacticVector):
    """A single lateral movement vector describing how an attacker could move through the environment."""

    movement_achieved: str = Field(
        ...,
        description=(
            "Description of what movement or access is achieved—"
            "e.g., 'Access to additional workspace', 'Cross-tenant resource access', "
            "'Access to connected system or service'."
        ),
    )


class LateralMovementExplorerInput(BaseModel):
    """Input for the lateral movement explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which lateral movement methods are most relevant",
    )


class LateralMovementExplorerOutput(BaseModel):
    """Output from the lateral movement explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[LateralMovementVector] = Field(
        description="All discovered lateral movement vectors for the application"
    )
    summary: str = Field(
        description="Summary of lateral movement findings and methods available from the starting position"
    )


# Collection Vector
class CollectionVector(TacticVector):
    """A single collection vector describing how an attacker could gather data of interest."""

    data_collected: str = Field(
        ...,
        description=(
            "Description of what data is collected—"
            "e.g., 'User profile information exported', 'Messages and communications retrieved', "
            "'Sensitive documents downloaded'."
        ),
    )


class CollectionExplorerInput(BaseModel):
    """Input for the collection explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which collection methods are most relevant",
    )


class CollectionExplorerOutput(BaseModel):
    """Output from the collection explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[CollectionVector] = Field(
        description="All discovered collection vectors for the application"
    )
    summary: str = Field(
        description="Summary of collection findings and methods available from the starting position"
    )


# Command and Control Vector
class CommandAndControlVector(TacticVector):
    """A single command and control vector describing how an attacker could establish communication channels."""

    communication_established: str = Field(
        ...,
        description=(
            "Description of what communication channel is established—"
            "e.g., 'Webhook endpoint registered for callback', 'External API connection established', "
            "'Outbound communication channel to attacker-controlled server'."
        ),
    )


class CommandAndControlExplorerInput(BaseModel):
    """Input for the command and control explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which command and control methods are most relevant",
    )


class CommandAndControlExplorerOutput(BaseModel):
    """Output from the command and control explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[CommandAndControlVector] = Field(
        description="All discovered command and control vectors for the application"
    )
    summary: str = Field(
        description="Summary of command and control findings and methods available from the starting position"
    )


# Exfiltration Vector
class ExfiltrationVector(TacticVector):
    """A single exfiltration vector describing how an attacker could steal and transfer data."""

    data_exfiltrated: str = Field(
        ...,
        description=(
            "Description of what data is exfiltrated—"
            "e.g., 'Bulk user data exported to external location', 'Sensitive files transferred to attacker server', "
            "'Database contents exfiltrated via API'."
        ),
    )


class ExfiltrationExplorerInput(BaseModel):
    """Input for the exfiltration explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which exfiltration methods are most relevant",
    )


class ExfiltrationExplorerOutput(BaseModel):
    """Output from the exfiltration explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[ExfiltrationVector] = Field(
        description="All discovered exfiltration vectors for the application"
    )
    summary: str = Field(
        description="Summary of exfiltration findings and methods available from the starting position"
    )


# Impact Vector
class ImpactVector(TacticVector):
    """A single impact vector describing how an attacker could manipulate, interrupt, or destroy systems."""

    impact_achieved: str = Field(
        ...,
        description=(
            "Description of what impact is achieved—"
            "e.g., 'Critical data deleted', 'Service availability disrupted', "
            "'System configuration corrupted', 'Account termination executed'."
        ),
    )


class ImpactExplorerInput(BaseModel):
    """Input for the impact explorer agent."""

    application_capabilities: ApplicationCapabilityAnalysis
    objective: Optional[str] = Field(
        default=None,
        description="Optional specific attacker objective that may inform which impact methods are most relevant",
    )


class ImpactExplorerOutput(BaseModel):
    """Output from the impact explorer agent."""

    model_config = ConfigDict(extra="forbid")

    application_name: str = Field(description="Name of the application being analyzed")
    vectors: list[ImpactVector] = Field(
        description="All discovered impact vectors for the application"
    )
    summary: str = Field(
        description="Summary of impact findings and methods available from the starting position"
    )
