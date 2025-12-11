from agents import Agent, ModelSettings, Runner
from agents.model_settings import Reasoning

from engine.models.audit_logs import DocumentationExtractionOutput
from engine.models.detections import DetectionAgentInput, DetectionAgentOutput
from engine.prompts.detection_agent import DETECTION_AGENT_PROMPT


def create_detection_agent():
    """Create a detection agent that analyzes whether techniques can be detected using audit logs.

    This factory function creates an agent that can analyze whether a specific MITRE ATT&CK
    technique and its method steps can be detected using the available audit logs from the
    audit log analysis.

    Returns:
        A configured detection agent
    """
    detection_agent = Agent(
        name="detection-agent",
        model="gpt-5.1",
        instructions=DETECTION_AGENT_PROMPT,
        output_type=DetectionAgentOutput,
        model_settings=ModelSettings(
            reasoning=Reasoning(
                effort="high",
                summary="detailed",
            ),
            parallel_tool_calls=True,
        ),
        tools=[],
    )

    return detection_agent


async def run_detection_analysis(
    technique_name: str,
    method_steps: list,
    audit_log_analysis: DocumentationExtractionOutput,
) -> DetectionAgentOutput:
    """
    Run the detection analysis workflow.

    This function analyzes whether a specific MITRE ATT&CK technique and its method steps
    can be detected using the available audit logs from the audit log analysis.

    Args:
        technique_name: The MITRE ATT&CK technique name
        method_steps: List of MethodStep objects describing how the technique is executed
        audit_log_analysis: Complete audit log analysis containing all available
                           audit log events, schemas, and integration options

    Returns:
        DetectionAgentOutput with detection analysis for the technique and method steps
    """
    # Create the detection agent
    detection_agent = create_detection_agent()

    # Prepare input
    input_data = DetectionAgentInput(
        technique_name=technique_name,
        method_steps=method_steps,
        audit_log_analysis=audit_log_analysis,
    )

    # Run the agent
    print(f"Running detection analysis for technique {technique_name} ...")
    result = await Runner.run(
        detection_agent,
        input_data.model_dump_json(),
        max_turns=50,
    )

    return result.final_output
