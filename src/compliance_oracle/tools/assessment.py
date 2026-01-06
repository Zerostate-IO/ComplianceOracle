"""Assessment tools for interview-style posture building.

Provides stateless question templates that agents can use to interview
users about control implementation, then translate answers into
ControlStatus values via the existing document_compliance tool.
"""

from fastmcp import FastMCP

from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.models.schemas import (
    AssessmentAnswerOption,
    AssessmentAnswerType,
    AssessmentQuestion,
    AssessmentTemplate,
    ControlStatus,
)


def register_assessment_tools(mcp: FastMCP) -> None:
    """Register assessment/interview tools with the MCP server."""

    @mcp.tool()
    async def get_assessment_questions(
        framework: str = "nist-csf-2.0",
        function: str | None = None,
        category: str | None = None,
        control_id: str | None = None,
        granularity: str = "standard",
    ) -> AssessmentTemplate:
        """Generate interview-style questions for assessing controls.

        This tool is intentionally stateless. It returns a set of structured
        questions that an agent can ask a human (or another system) in order
        to assess implementation status for controls in a given scope.

        The caller is expected to:
        - Ask the questions in sequence
        - Normalize the answers to the provided option values (when applicable)
        - Call document_compliance() separately to record direct status

        Args:
            framework: Framework ID (e.g., "nist-csf-2.0").
            function: Optional function ID to filter controls (e.g., "PR").
            category: Optional category ID to filter controls (e.g., "PR.AC").
            control_id: Optional single control to focus on.
            granularity: Currently reserved; "standard" emits one status
                question per control in scope.

        Returns:
            AssessmentTemplate describing the questions to ask.
        """

        manager = FrameworkManager()

        # Determine control scope
        controls = []
        if control_id is not None:
            all_controls = await manager.list_controls(
                framework_id=framework,
                function_id=function,
                category_id=category,
            )
            controls = [c for c in all_controls if c.id == control_id]
        else:
            controls = await manager.list_controls(
                framework_id=framework,
                function_id=function,
                category_id=category,
            )

        control_ids = [c.id for c in controls]
        questions: list[AssessmentQuestion] = []

        # For now, granularity is a no-op; we always emit a single status
        # question per control.
        for ctrl in controls:
            question = AssessmentQuestion(
                id=f"{ctrl.id}-status",
                framework_id=framework,
                control_ids=[ctrl.id],
                text=(
                    f"For control {ctrl.id} ({ctrl.name}), how would you rate "
                    "its implementation in your environment?"
                ),
                answer_type=AssessmentAnswerType.CHOICE,
                answer_options=[
                    AssessmentAnswerOption(
                        value="implemented",
                        label="Implemented",
                        maps_to_status=ControlStatus.IMPLEMENTED,
                    ),
                    AssessmentAnswerOption(
                        value="partial",
                        label="Partially implemented",
                        maps_to_status=ControlStatus.PARTIAL,
                    ),
                    AssessmentAnswerOption(
                        value="planned",
                        label="Planned",
                        maps_to_status=ControlStatus.PLANNED,
                    ),
                    AssessmentAnswerOption(
                        value="not_applicable",
                        label="Not applicable",
                        maps_to_status=ControlStatus.NOT_APPLICABLE,
                    ),
                    AssessmentAnswerOption(
                        value="not_addressed",
                        label="Not addressed",
                        maps_to_status=ControlStatus.NOT_ADDRESSED,
                    ),
                ],
            )
            questions.append(question)

        # Scope metadata for the template
        scope = "framework"
        if control_id is not None:
            scope = "control"
        elif category is not None:
            scope = "category"
        elif function is not None:
            scope = "function"

        template = AssessmentTemplate(
            framework_id=framework,
            scope=scope,
            function_id=function,
            category_id=category,
            control_ids=control_ids,
            questions=questions,
        )

        return template
