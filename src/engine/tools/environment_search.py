from typing import List

from agents.tool import function_tool

from engine.models.attack_paths import EnvironmentConstraint


def get_environment_constraints() -> List[dict]:
    """Get environment constraints that may affect initial access vectors.

    Returns:
        List[dict]: A list of environment constraints with name, description, and relevance.
    """
    # Hardcoded constraints for now
    constraints = [
        EnvironmentConstraint(
            name="MFA Required",
            description="Multi-factor authentication (MFA) is required for all user accounts. Users must authenticate using a second factor (SMS, authenticator app, hardware token) in addition to password.",
            relevance="Relevant when exploring initial access vectors that rely on credential-based authentication. MFA may block password-based attacks, credential stuffing, or brute force attempts unless the attacker can bypass or compromise the second factor.",
        ),
        EnvironmentConstraint(
            name="IP Allowlisting",
            description="The application restricts access to specific IP addresses or IP ranges. Only connections from allowlisted IPs are permitted.",
            relevance="Relevant for any initial access vector that requires network access to the application. Attackers must either compromise an allowlisted IP, use VPN/proxy services that match allowlisted ranges, or find ways to bypass IP restrictions.",
        ),
        EnvironmentConstraint(
            name="SSO-Only Authentication",
            description="The application only supports Single Sign-On (SSO) authentication. Users cannot create local accounts or use password-based login. All authentication flows through an identity provider (IdP).",
            relevance="Relevant when exploring credential-based initial access. Attackers cannot use local account registration or password attacks. They must compromise the IdP, abuse SSO flows, or exploit SSO misconfigurations.",
        ),
        EnvironmentConstraint(
            name="Domain-Based Registration",
            description="User registration is restricted to specific email domains. Only users with email addresses from approved domains can create accounts.",
            relevance="Relevant for initial access vectors involving account registration. Attackers cannot register arbitrary accounts unless they control or compromise an approved email domain.",
        ),
        EnvironmentConstraint(
            name="Rate Limiting",
            description="The application implements strict rate limiting on authentication endpoints, API calls, and registration flows. Excessive requests result in temporary or permanent IP bans.",
            relevance="Relevant for brute force attacks, credential stuffing, enumeration, or automated registration attempts. Attackers must use low-and-slow techniques or find ways to bypass rate limits.",
        ),
        EnvironmentConstraint(
            name="CAPTCHA Protection",
            description="CAPTCHA challenges are required for registration, login, and certain API endpoints to prevent automated attacks.",
            relevance="Relevant for automated initial access vectors such as credential stuffing, automated registration, or API abuse. Attackers must solve CAPTCHAs manually or use CAPTCHA-solving services.",
        ),
        EnvironmentConstraint(
            name="Email Verification Required",
            description="New account registrations require email verification. Users must click a verification link sent to their email address before the account is activated.",
            relevance="Relevant for registration-based initial access vectors. Attackers must control or compromise the target email address to complete registration, or find ways to bypass email verification.",
        ),
        EnvironmentConstraint(
            name="Admin Approval Required",
            description="New user registrations require manual approval by an administrator before accounts are activated.",
            relevance="Relevant for registration-based initial access. Attackers cannot immediately gain access through registration unless they can impersonate legitimate users or compromise the approval process.",
        ),
    ]

    return [constraint.model_dump() for constraint in constraints]


@function_tool
def get_environment_constraints_tool() -> list[dict]:
    """Get environment constraints that may affect initial access vectors.

    Use this tool to understand environmental constraints that could impact
    the feasibility of initial access vectors. When exploring a specific vector,
    check if any constraints are relevant and adjust your analysis accordingly.

    Returns:
        List[dict]: A list of environment constraints, each containing:
            - name: Name of the constraint
            - description: Detailed description of the constraint
            - relevance: When and how this constraint is relevant to initial access

    Example usage:
        - Before exploring credential-based attacks, check for MFA or SSO constraints
        - Before exploring registration-based attacks, check for domain restrictions or approval requirements
        - Before exploring automated attacks, check for rate limiting or CAPTCHA constraints
    """
    return get_environment_constraints()
