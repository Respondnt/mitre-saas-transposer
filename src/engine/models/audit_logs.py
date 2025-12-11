from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AuditLogInput(BaseModel):
    urls: list[str]
    relevant_sitemap_urls: list[str] | None = None


class PlanOrTier(BaseModel):
    name: str = Field(
        description="Name of the commercial plan, product tier, or subscription (e.g. Enterprise, Business Plus).",
    )
    description: Optional[str] = Field(
        default=None,
        description="Short description of what this plan or tier includes, taken from the documentation.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Any additional notes about this plan or tier (e.g. regional availability, legacy status).",
    )


class PermissionOrRole(BaseModel):
    name: str = Field(
        description="Name of the permission, role, or access level required to use the feature.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Explanation of what this permission or role allows in the context of the feature.",
    )


class LicenseRequired(BaseModel):
    plans_or_tiers: Optional[List[PlanOrTier]] = Field(
        default=None,
        description="List of commercial plans or product tiers required to access the feature.",
    )
    permissions_or_roles: Optional[List[PermissionOrRole]] = Field(
        default=None,
        description="List of specific roles or permissions required in addition to a plan or tier.",
    )
    other_requirements: Optional[List[str]] = Field(
        default=None,
        description="Any other licensing or access requirements mentioned (e.g. add-ons, betas, partner-only).",
    )


class Event(BaseModel):
    name: str = Field(
        description="Exact name of the log, event, or action as written in the documentation.",
    )
    type: Optional[str] = Field(
        default=None,
        description="Optional event type or category label as given in the source (e.g. audit, access, admin).",
    )
    description: Optional[str] = Field(
        default=None,
        description="Summary of what this event represents or when it is emitted.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Any extra context or caveats about this event (e.g. limitations, sampling, delays).",
    )


class EventGroup(BaseModel):
    group_name: str = Field(
        description="Logical group name for a set of events, mirroring how the source groups them.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Short explanation of what this event group represents.",
    )
    events: List[Event] = Field(
        description="All events that belong to this logical group.",
    )


class AvailableLogsOrEvents(BaseModel):
    groups: Optional[List[EventGroup]] = Field(
        default=None,
        description="List of event groups when the documentation groups events under named sections.",
    )
    ungrouped_events: Optional[List[Event]] = Field(
        default=None,
        description="Events that are not explicitly grouped in the documentation.",
    )


class ApiIntegration(BaseModel):
    name: str = Field(
        description="Name or label of the API-based integration option.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Summary of what this API integration does or how it is used.",
    )
    endpoint_or_reference: Optional[str] = Field(
        default=None,
        description="Endpoint path, API route, or reference identifier as stated in the documentation.",
    )


class WebhookIntegration(BaseModel):
    name: str = Field(
        description="Name or label of the webhook-based integration option.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Summary of what this webhook delivers or when it fires.",
    )
    target_or_payload_reference: Optional[str] = Field(
        default=None,
        description="Details about the webhook target, payload schema, or configuration reference.",
    )


class SiemOrSecurityIntegration(BaseModel):
    name: str = Field(
        description="Name of the SIEM or security platform integration (e.g. Splunk, QRadar).",
    )
    description: Optional[str] = Field(
        default=None,
        description="Explanation of how this SIEM/security integration works or what data it receives.",
    )


class CloudServiceIntegration(BaseModel):
    name: str = Field(
        description="Name of the cloud service integration (e.g. AWS EventBridge, GCP Pub/Sub).",
    )
    description: Optional[str] = Field(
        default=None,
        description="Summary of how this cloud service is used to export or route logs/events.",
    )


class UiExport(BaseModel):
    name: str = Field(
        description="Name of the UI-based export option (e.g. CSV export, download button).",
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of how the export works from the product UI.",
    )


class AutomationOrOtherIntegration(BaseModel):
    name: str = Field(
        description="Name or label of any automation or 'other' integration option not covered above.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Explanation of how this integration works or what automation it enables.",
    )


class Integrations(BaseModel):
    apis: Optional[List[ApiIntegration]] = Field(
        default=None,
        description="All API-based integration options described in the documentation.",
    )
    webhooks: Optional[List[WebhookIntegration]] = Field(
        default=None,
        description="All webhook-based integration options described in the documentation.",
    )
    siem_or_security_integrations: Optional[List[SiemOrSecurityIntegration]] = Field(
        default=None,
        description="Integrations with SIEM or other security platforms.",
    )
    cloud_services: Optional[List[CloudServiceIntegration]] = Field(
        default=None,
        description="Integrations using cloud-native services such as EventBridge or Pub/Sub.",
    )
    ui_exports: Optional[List[UiExport]] = Field(
        default=None,
        description="UI-based export mechanisms available in the product.",
    )
    automation_or_other_integrations: Optional[List[AutomationOrOtherIntegration]] = (
        Field(
            default=None,
            description="Any other integration or automation methods that do not fit the other categories.",
        )
    )


class DocumentationExtractionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    license_required: LicenseRequired = Field(
        description="Structured summary of licensing, plan, and access requirements for the feature.",
    )
    available_logs_or_events: AvailableLogsOrEvents = Field(
        description="Structured catalogue of all logs, events, or actions described in the documentation.",
    )
    integrations: Integrations = Field(
        description="Structured summary of all integration and export options.",
    )
    schema_yaml: Optional[str] = Field(
        default=None,
        description="Complete global audit log schema in YAML format if available in the documentation. This represents the overall schema structure for all audit logs in the application, including all fields, types, nested structures, and schema definitions as documented.",
    )
    references: List[str] = Field(
        description="List of source documentation URLs that were used to derive this output.",
    )
