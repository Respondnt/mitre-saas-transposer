import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SourceReference(BaseModel):
    name: str = Field(
        ...,
        description="Human-readable name of the source, such as a document, page, or system.",
    )
    url: Optional[str] = Field(
        default=None,
        description="Optional URL where this source can be accessed or referenced.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Short description of what this source covers or why it is relevant.",
    )


class EvidenceReference(BaseModel):
    title: str = Field(..., description="Title or identifier for the evidence item.")
    url: Optional[str] = Field(
        default=None,
        description="Optional URL pointing to the specific section or document used as evidence.",
    )
    summary: Optional[str] = Field(
        default=None,
        description="Optional short summary of what this evidence shows.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional free-form notes about how this evidence was interpreted or used.",
    )


class InterfaceChannel(str, Enum):
    ui = "ui"
    api = "api"
    cli = "cli"
    integration = "integration"
    webhook = "webhook"
    other = "other"


class InterfaceReference(BaseModel):
    channel: InterfaceChannel = Field(
        ...,
        description="Type of interface through which the capability is accessed (UI, API, CLI, etc.).",
    )
    details: str = Field(
        ...,
        description="Human-readable description of how this interface is used (paths, pages, commands, etc.).",
    )
    url: Optional[str] = Field(
        default=None,
        description="Optional URL for this specific interface, such as a UI page or API endpoint docs.",
    )


class Capability(BaseModel):
    name: str = Field(..., description="Short name for the capability or feature.")
    description: str = Field(
        ...,
        description="1–3 sentence description of what this capability does and how it behaves.",
    )
    primary_actors: List[str] = Field(
        ...,
        description="User roles or system actors that primarily use or trigger this capability.",
    )
    main_interfaces: List[InterfaceReference] = Field(
        ...,
        description="Key entry points or interfaces (UI pages, API endpoints, webhooks, etc.) for this capability.",
    )
    key_data_involved: List[str] = Field(
        ...,
        description="Important data elements, identifiers, or records handled by this capability.",
    )
    security_relevant_traits: List[str] = Field(
        ...,
        description="Attributes of this capability that matter for security (privilege level, cross-tenant effects, etc.).",
    )
    evidence: List[EvidenceReference] = Field(
        ...,
        description="References to documentation or other sources that describe this capability.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional free-form notes, caveats, or implementation details for this capability.",
    )


class NamedItem(BaseModel):
    name: str = Field(
        ..., description="Name of the component, system, or data-flow element."
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional description of the item’s role or behaviour in the system.",
    )


class OpenQuestion(BaseModel):
    question: str = Field(
        ...,
        description="A specific unresolved question or ambiguity discovered during analysis.",
    )
    context: Optional[str] = Field(
        default=None,
        description="Optional context or excerpt from docs that led to this question.",
    )
    related_capabilities: Optional[List[str]] = Field(
        default=None,
        description="Optional list of capability names that this question relates to.",
    )


class CoverageOverview(BaseModel):
    sources_analysed: List[SourceReference] = Field(
        ...,
        description="List of documentation sources or systems that were actually analysed.",
    )
    likely_uncovered_areas_or_ambiguities: List[str] = Field(
        ...,
        description="Areas that are likely missing, incomplete, or unclear based on available docs.",
    )
    assumptions_made: List[str] = Field(
        ...,
        description="Explicit assumptions recorded to compensate for gaps or ambiguities in coverage.",
    )


class CapabilityMap(BaseModel):
    core_product_capabilities: List[Capability] = Field(
        ...,
        description="Capabilities that represent core, user-facing product functionality.",
    )
    administrative_and_operational_capabilities: List[Capability] = Field(
        ...,
        description="Capabilities used for administration, configuration, and operational tasks.",
    )
    api_surface_and_integrations: List[Capability] = Field(
        ...,
        description="Capabilities that expose or consume APIs, webhooks, or external integrations.",
    )
    background_jobs_and_automation: List[Capability] = Field(
        ...,
        description="Capabilities implemented as background tasks, scheduled jobs, or automated workflows.",
    )


class TechnicalComponentsAndDataFlows(BaseModel):
    services_or_modules: List[NamedItem] = Field(
        ...,
        description="Application services or modules that make up the system’s architecture.",
    )
    storage_and_logs: List[NamedItem] = Field(
        ...,
        description="Data stores, log stores, or other persistence layers described in the docs.",
    )
    external_systems: List[NamedItem] = Field(
        ...,
        description="Third-party or external systems that this application interacts with.",
    )
    data_flows: List[NamedItem] = Field(
        ...,
        description="High-level data flows or pipelines between components and systems.",
    )


class SecurityRelevantBehaviours(BaseModel):
    privileged_operations: List[str] = Field(
        ...,
        description="Operations that require elevated privileges or have significant security impact.",
    )
    user_configurable_logic: List[str] = Field(
        ...,
        description="Places where users or admins can configure logic, rules, or workflows.",
    )
    auth_and_identity_behaviours: List[str] = Field(
        ...,
        description="Behaviours related to authentication, authorization, and identity handling.",
    )
    logging_and_audit_behaviours: List[str] = Field(
        ...,
        description="How the system logs, audits, and records security-relevant events.",
    )
    failure_modes: List[str] = Field(
        ...,
        description="Known or described failure modes, including how the system behaves under error conditions.",
    )


class ApplicationCapabilityAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    application_name: Optional[str] = Field(
        default=None,
        description="Optional human-readable name of the application being analysed.",
    )
    generated_at: Optional[datetime.datetime] = Field(
        default=None,
        description="Optional timestamp when this analysis object was generated.",
    )
    coverage_overview: CoverageOverview = Field(
        ...,
        description="Summary of which sources were analysed and what gaps or assumptions remain.",
    )
    capability_map: CapabilityMap = Field(
        ...,
        description="Structured capabilities grouped by core product, admin, API, and automation.",
    )
    technical_components_and_data_flows: TechnicalComponentsAndDataFlows = Field(
        ...,
        description="Technical view of services, storage, external systems, and data flows.",
    )
    security_relevant_behaviours: SecurityRelevantBehaviours = Field(
        ...,
        description="Descriptive list of security-relevant behaviours observed in the application.",
    )
    open_questions: List[OpenQuestion] = Field(
        ...,
        description="Open questions or ambiguities about this capability.",
    )
    evidence_index: List[EvidenceReference] = Field(
        ...,
        description="Index of evidence items and references that support the analysis.",
    )


class AppBreakdownInput(BaseModel):
    urls: list[str]
    site_map_urls: list[str]
