"""Tests for evaluation tools (evaluate_compliance)."""

from unittest.mock import patch

import pytest

from compliance_oracle.models.schemas import (
    ControlDetails,
    SearchResult,
    Severity,
)


class TestEvaluateCompliance:
    """Tests for evaluate_compliance tool."""

    @pytest.mark.asyncio
    async def test_evaluate_compliance_happy_path(
        self,
        mock_framework_manager,
        mock_control_searcher,
    ) -> None:
        """Test evaluate_compliance returns findings for content gaps."""
        # Setup search results
        search_result = SearchResult(
            control_id="PR.AC-01",
            control_name="Identity and Credentials",
            description="Manage user identities and credentials using automated tools.",
            framework_id="nist-csf-2.0",
            relevance_score=0.85,
        )
        mock_control_searcher.search.return_value = [search_result]
        mock_control_searcher.is_indexed.return_value = True

        # Setup control details
        control_details = ControlDetails(
            id="PR.AC-01",
            name="Identity and Credentials",
            description="Manage user identities and credentials using automated tools.",
            framework_id="nist-csf-2.0",
            function_id="PR",
            function_name="PROTECT",
            category_id="PR.AC",
            category_name="Identity Management and Access Control",
            implementation_examples=["Implement MFA"],
            informative_references=[],
            keywords=[],
            related_controls=[],
            mappings={},
        )
        mock_framework_manager.get_control_details.return_value = control_details

        # Content without identity management references
        content = "Our application stores data in a database and provides a REST API."

        # Patch the managers
        with (
            patch(
                "compliance_oracle.tools.evaluation.FrameworkManager",
                return_value=mock_framework_manager,
            ),
            patch(
                "compliance_oracle.tools.evaluation.ControlSearcher",
                return_value=mock_control_searcher,
            ),
        ):
            from compliance_oracle.tools.evaluation import evaluate_compliance

            result = await evaluate_compliance(
                content=content,
                content_type="design_doc",
                framework="nist-csf-2.0",
            )

        assert result["framework"] == "nist-csf-2.0"
        assert result["findings_count"] >= 0
        assert result["evaluated_controls"] >= 1
        assert isinstance(result["findings"], list)
        assert isinstance(result["compliant_areas"], list)

    @pytest.mark.asyncio
    async def test_evaluate_compliance_with_compliant_content(
        self,
        mock_framework_manager,
        mock_control_searcher,
    ) -> None:
        """Test evaluate_compliance identifies compliant areas."""
        # Setup search results for access control
        search_result = SearchResult(
            control_id="PR.AC-01",
            control_name="Identity and Credentials",
            description="Manage user identities and credentials.",
            framework_id="nist-csf-2.0",
            relevance_score=0.90,
        )
        mock_control_searcher.search.return_value = [search_result]
        mock_control_searcher.is_indexed.return_value = True

        control_details = ControlDetails(
            id="PR.AC-01",
            name="Identity and Credentials",
            description="Manage user identities and credentials.",
            framework_id="nist-csf-2.0",
            function_id="PR",
            function_name="PROTECT",
            category_id="PR.AC",
            category_name="Identity Management and Access Control",
            implementation_examples=[],
            informative_references=[],
            keywords=[],
            related_controls=[],
            mappings={},
        )
        mock_framework_manager.get_control_details.return_value = control_details

        # Content WITH MFA reference (should be compliant for PR.AC)
        content = "Our application uses multi-factor authentication (MFA) for all user logins."

        with (
            patch(
                "compliance_oracle.tools.evaluation.FrameworkManager",
                return_value=mock_framework_manager,
            ),
            patch(
                "compliance_oracle.tools.evaluation.ControlSearcher",
                return_value=mock_control_searcher,
            ),
        ):
            from compliance_oracle.tools.evaluation import evaluate_compliance

            result = await evaluate_compliance(
                content=content,
                content_type="design_doc",
                framework="nist-csf-2.0",
            )

        # Should identify compliant areas
        assert result["framework"] == "nist-csf-2.0"
        assert len(result["compliant_areas"]) > 0
        # PR.AC should be in compliant areas since content mentions MFA
        compliant_text = " ".join(result["compliant_areas"])
        assert "PR.AC" in compliant_text or "MFA" in compliant_text

    @pytest.mark.asyncio
    async def test_evaluate_compliance_with_focus_areas(
        self,
        mock_framework_manager,
        mock_control_searcher,
    ) -> None:
        """Test evaluate_compliance respects focus_areas parameter."""
        search_result = SearchResult(
            control_id="PR.DS-01",
            control_name="Data Security",
            description="Data-at-rest protection.",
            framework_id="nist-csf-2.0",
            relevance_score=0.80,
        )
        mock_control_searcher.search.return_value = [search_result]
        mock_control_searcher.is_indexed.return_value = True

        control_details = ControlDetails(
            id="PR.DS-01",
            name="Data Security",
            description="Data-at-rest protection.",
            framework_id="nist-csf-2.0",
            function_id="PR",
            function_name="PROTECT",
            category_id="PR.DS",
            category_name="Data Security",
            implementation_examples=[],
            informative_references=[],
            keywords=[],
            related_controls=[],
            mappings={},
        )
        mock_framework_manager.get_control_details.return_value = control_details

        content = "System architecture document without encryption details."

        with (
            patch(
                "compliance_oracle.tools.evaluation.FrameworkManager",
                return_value=mock_framework_manager,
            ),
            patch(
                "compliance_oracle.tools.evaluation.ControlSearcher",
                return_value=mock_control_searcher,
            ),
        ):
            from compliance_oracle.tools.evaluation import evaluate_compliance

            result = await evaluate_compliance(
                content=content,
                content_type="design_doc",
                framework="nist-csf-2.0",
                focus_areas=["PR"],
            )

        assert result["framework"] == "nist-csf-2.0"
        # Verify search was called with PR-related query
        mock_control_searcher.search.assert_called()

    @pytest.mark.asyncio
    async def test_evaluate_compliance_different_content_types(
        self,
        mock_framework_manager,
        mock_control_searcher,
    ) -> None:
        """Test evaluate_compliance handles different content types."""
        search_result = SearchResult(
            control_id="PR.AC-01",
            control_name="Identity and Credentials",
            description="Manage identities.",
            framework_id="nist-csf-2.0",
            relevance_score=0.75,
        )
        mock_control_searcher.search.return_value = [search_result]
        mock_control_searcher.is_indexed.return_value = True

        control_details = ControlDetails(
            id="PR.AC-01",
            name="Identity and Credentials",
            description="Manage identities.",
            framework_id="nist-csf-2.0",
            function_id="PR",
            function_name="PROTECT",
            category_id="PR.AC",
            category_name="Identity Management and Access Control",
            implementation_examples=[],
            informative_references=[],
            keywords=[],
            related_controls=[],
            mappings={},
        )
        mock_framework_manager.get_control_details.return_value = control_details

        code_content = """
        def authenticate(user, password):
            return check_password(user, password)
        """

        with (
            patch(
                "compliance_oracle.tools.evaluation.FrameworkManager",
                return_value=mock_framework_manager,
            ),
            patch(
                "compliance_oracle.tools.evaluation.ControlSearcher",
                return_value=mock_control_searcher,
            ),
        ):
            from compliance_oracle.tools.evaluation import evaluate_compliance

            result = await evaluate_compliance(
                content=code_content,
                content_type="code",
                framework="nist-csf-2.0",
            )

        assert result["framework"] == "nist-csf-2.0"

    @pytest.mark.asyncio
    async def test_evaluate_compliance_architecture_content(
        self,
        mock_framework_manager,
        mock_control_searcher,
    ) -> None:
        """Test evaluate_compliance with architecture content type."""
        search_result = SearchResult(
            control_id="DE.CM-01",
            control_name="Continuous Monitoring",
            description="Monitor for cybersecurity events.",
            framework_id="nist-csf-2.0",
            relevance_score=0.70,
        )
        mock_control_searcher.search.return_value = [search_result]
        mock_control_searcher.is_indexed.return_value = True

        control_details = ControlDetails(
            id="DE.CM-01",
            name="Continuous Monitoring",
            description="Monitor for cybersecurity events.",
            framework_id="nist-csf-2.0",
            function_id="DE",
            function_name="DETECT",
            category_id="DE.CM",
            category_name="Continuous Monitoring",
            implementation_examples=[],
            informative_references=[],
            keywords=[],
            related_controls=[],
            mappings={},
        )
        mock_framework_manager.get_control_details.return_value = control_details

        arch_content = """
        Architecture:
        - Web tier: Load balancers
        - App tier: Kubernetes clusters
        - Data tier: PostgreSQL replicas
        """

        with (
            patch(
                "compliance_oracle.tools.evaluation.FrameworkManager",
                return_value=mock_framework_manager,
            ),
            patch(
                "compliance_oracle.tools.evaluation.ControlSearcher",
                return_value=mock_control_searcher,
            ),
        ):
            from compliance_oracle.tools.evaluation import evaluate_compliance

            result = await evaluate_compliance(
                content=arch_content,
                content_type="architecture",
                framework="nist-csf-2.0",
            )

        assert result["framework"] == "nist-csf-2.0"

    @pytest.mark.asyncio
    async def test_evaluate_compliance_framework_not_indexed(
        self,
        mock_framework_manager,
        mock_control_searcher,
    ) -> None:
        """Test evaluate_compliance handles unindexed framework."""
        mock_control_searcher.is_indexed.return_value = False
        mock_control_searcher.index_framework.return_value = 0  # No controls indexed

        content = "Some design document content."

        with (
            patch(
                "compliance_oracle.tools.evaluation.FrameworkManager",
                return_value=mock_framework_manager,
            ),
            patch(
                "compliance_oracle.tools.evaluation.ControlSearcher",
                return_value=mock_control_searcher,
            ),
        ):
            from compliance_oracle.tools.evaluation import evaluate_compliance

            result = await evaluate_compliance(
                content=content,
                content_type="design_doc",
                framework="unknown-framework",
            )

        assert result["framework"] == "unknown-framework"
        assert result["findings_count"] == 0
        assert result["evaluated_controls"] == 0
        assert "error" in result

    @pytest.mark.asyncio
    async def test_evaluate_compliance_auto_indexes(
        self,
        mock_framework_manager,
        mock_control_searcher,
    ) -> None:
        """Test evaluate_compliance auto-indexes framework if not indexed."""
        search_result = SearchResult(
            control_id="PR.AC-01",
            control_name="Identity and Credentials",
            description="Manage identities.",
            framework_id="nist-csf-2.0",
            relevance_score=0.80,
        )
        mock_control_searcher.search.return_value = [search_result]
        mock_control_searcher.is_indexed.return_value = False  # Not indexed initially
        mock_control_searcher.index_framework.return_value = 100  # Then indexed

        control_details = ControlDetails(
            id="PR.AC-01",
            name="Identity and Credentials",
            description="Manage identities.",
            framework_id="nist-csf-2.0",
            function_id="PR",
            function_name="PROTECT",
            category_id="PR.AC",
            category_name="Identity Management and Access Control",
            implementation_examples=[],
            informative_references=[],
            keywords=[],
            related_controls=[],
            mappings={},
        )
        mock_framework_manager.get_control_details.return_value = control_details

        content = "Design document content."

        with (
            patch(
                "compliance_oracle.tools.evaluation.FrameworkManager",
                return_value=mock_framework_manager,
            ),
            patch(
                "compliance_oracle.tools.evaluation.ControlSearcher",
                return_value=mock_control_searcher,
            ),
        ):
            from compliance_oracle.tools.evaluation import evaluate_compliance

            result = await evaluate_compliance(
                content=content,
                content_type="design_doc",
                framework="nist-csf-2.0",
            )

        # Should have tried to index
        mock_control_searcher.index_framework.assert_called_once_with("nist-csf-2.0")
        assert result["framework"] == "nist-csf-2.0"

    @pytest.mark.asyncio
    async def test_evaluate_compliance_invalid_content_type(
        self,
        mock_framework_manager,
        mock_control_searcher,
    ) -> None:
        """Test evaluate_compliance handles invalid content_type gracefully."""
        mock_control_searcher.is_indexed.return_value = True
        mock_control_searcher.search.return_value = []

        content = "Some content."

        with (
            patch(
                "compliance_oracle.tools.evaluation.FrameworkManager",
                return_value=mock_framework_manager,
            ),
            patch(
                "compliance_oracle.tools.evaluation.ControlSearcher",
                return_value=mock_control_searcher,
            ),
        ):
            from compliance_oracle.tools.evaluation import evaluate_compliance

            # Should not raise, defaults to design_doc
            result = await evaluate_compliance(
                content=content,
                content_type="invalid_type",
                framework="nist-csf-2.0",
            )

        assert result["framework"] == "nist-csf-2.0"

    @pytest.mark.asyncio
    async def test_evaluate_compliance_empty_content(
        self,
        mock_framework_manager,
        mock_control_searcher,
    ) -> None:
        """Test evaluate_compliance with empty content."""
        mock_control_searcher.is_indexed.return_value = True
        mock_control_searcher.search.return_value = []

        content = ""

        with (
            patch(
                "compliance_oracle.tools.evaluation.FrameworkManager",
                return_value=mock_framework_manager,
            ),
            patch(
                "compliance_oracle.tools.evaluation.ControlSearcher",
                return_value=mock_control_searcher,
            ),
        ):
            from compliance_oracle.tools.evaluation import evaluate_compliance

            result = await evaluate_compliance(
                content=content,
                content_type="design_doc",
                framework="nist-csf-2.0",
            )

        assert result["framework"] == "nist-csf-2.0"
        # Empty content should have no compliant areas
        assert result["compliant_areas"] == []


class TestComplianceFinding:
    """Tests for ComplianceFinding model."""

    def test_compliance_finding_creation(self) -> None:
        """Test ComplianceFinding can be created with all fields."""
        from compliance_oracle.models.schemas import ComplianceFinding

        finding = ComplianceFinding(
            control_id="PR.AC-01",
            control_name="Identity and Credentials",
            function="PROTECT",
            category="Identity Management and Access Control",
            finding="No evidence found in design document addressing Identity and Credentials",
            rationale="CSF PR.AC-01 requires: Manage identities. The evaluated design document does not demonstrate coverage.",
            severity=Severity.HIGH,
        )

        assert finding.control_id == "PR.AC-01"
        assert finding.severity == Severity.HIGH
        assert "Identity" in finding.finding

    def test_compliance_finding_severity_values(self) -> None:
        """Test ComplianceFinding accepts all severity values."""
        from compliance_oracle.models.schemas import ComplianceFinding

        for severity in [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]:
            finding = ComplianceFinding(
                control_id="PR.AC-01",
                control_name="Test",
                function="PROTECT",
                category="Test Category",
                finding="Test finding",
                rationale="Test rationale",
                severity=severity,
            )
            assert finding.severity == severity


class TestEvaluationResponse:
    """Tests for EvaluationResponse model."""

    def test_evaluation_response_creation(self) -> None:
        """Test EvaluationResponse can be created with all fields."""
        from compliance_oracle.models.schemas import (
            ComplianceFinding,
            EvaluationResponse,
        )

        finding = ComplianceFinding(
            control_id="PR.AC-01",
            control_name="Identity and Credentials",
            function="PROTECT",
            category="Identity Management and Access Control",
            finding="Gap identified",
            rationale="Rationale here",
            severity=Severity.HIGH,
        )

        response = EvaluationResponse(
            framework="nist-csf-2.0",
            findings_count=1,
            findings=[finding],
            evaluated_controls=15,
            compliant_areas=["Data encryption at rest"],
        )

        assert response.framework == "nist-csf-2.0"
        assert response.findings_count == 1
        assert len(response.findings) == 1
        assert response.evaluated_controls == 15
        assert len(response.compliant_areas) == 1

    def test_evaluation_response_empty_findings(self) -> None:
        """Test EvaluationResponse with no findings."""
        from compliance_oracle.models.schemas import EvaluationResponse

        response = EvaluationResponse(
            framework="nist-csf-2.0",
            findings_count=0,
            findings=[],
            evaluated_controls=10,
            compliant_areas=[],
        )

        assert response.findings_count == 0
        assert response.findings == []


class TestSeverityDetermination:
    """Tests for severity determination logic."""

    def test_determine_severity_critical_category(self) -> None:
        """Test critical categories get critical/high severity."""
        from compliance_oracle.tools.evaluation import _determine_severity

        # PR.AC is a critical category
        severity = _determine_severity("PR.AC-01", 0.9)
        assert severity == Severity.CRITICAL

        severity = _determine_severity("PR.AC-01", 0.7)
        assert severity == Severity.HIGH

    def test_determine_severity_by_function(self) -> None:
        """Test severity is determined by function for non-critical categories."""
        from compliance_oracle.tools.evaluation import _determine_severity

        # PR function -> HIGH
        severity = _determine_severity("PR.IP-01", 0.7)
        assert severity == Severity.HIGH

        # DE function -> MEDIUM
        severity = _determine_severity("DE.CM-01", 0.7)
        assert severity == Severity.MEDIUM

    def test_determine_severity_adjusts_by_relevance(self) -> None:
        """Test severity adjusts based on relevance score."""
        from compliance_oracle.tools.evaluation import _determine_severity

        # High relevance can boost medium to high
        severity = _determine_severity("DE.CM-01", 0.95)
        assert severity == Severity.HIGH

        # Low relevance can reduce high to medium
        severity = _determine_severity("PR.IP-01", 0.4)
        assert severity == Severity.MEDIUM


class TestCompliantAreasDetection:
    """Tests for compliant area detection."""

    def test_find_compliant_areas_mfa(self) -> None:
        """Test detection of MFA compliance indicator."""
        from compliance_oracle.tools.evaluation import _find_compliant_areas

        content = "Our system uses multi-factor authentication for all users."
        areas = _find_compliant_areas(content, content.lower())

        assert len(areas) > 0
        assert any("PR.AC" in area for area in areas)

    def test_find_compliant_areas_encryption(self) -> None:
        """Test detection of encryption compliance indicator."""
        from compliance_oracle.tools.evaluation import _find_compliant_areas

        content = "All data is encrypted at rest using AES-256."
        areas = _find_compliant_areas(content, content.lower())

        assert len(areas) > 0
        assert any("PR.DS" in area for area in areas)

    def test_find_compliant_areas_monitoring(self) -> None:
        """Test detection of monitoring compliance indicator."""
        from compliance_oracle.tools.evaluation import _find_compliant_areas

        content = "We use SIEM for continuous monitoring and alerting."
        areas = _find_compliant_areas(content, content.lower())

        assert len(areas) > 0
        assert any("DE.CM" in area for area in areas)

    def test_find_compliant_areas_no_matches(self) -> None:
        """Test empty result when no compliance indicators found."""
        from compliance_oracle.tools.evaluation import _find_compliant_areas

        content = "This is a basic document with no security details."
        areas = _find_compliant_areas(content, content.lower())

        assert len(areas) == 0

    def test_find_compliant_areas_multiple_indicators(self) -> None:
        """Test detection of multiple compliance indicators."""
        from compliance_oracle.tools.evaluation import _find_compliant_areas

        content = """
        Our system uses MFA for authentication.
        All data is encrypted at rest and in transit.
        We have a SIEM for monitoring and alerting.
        """
        areas = _find_compliant_areas(content, content.lower())

        # Should detect PR.AC (MFA), PR.DS (encryption), DE.CM (monitoring)
        assert len(areas) >= 2


class TestFindingGeneration:
    """Tests for finding generation."""

    @pytest.mark.asyncio
    async def test_generate_finding_design_doc(self) -> None:
        """Test finding generation for design_doc content type."""
        from compliance_oracle.tools.evaluation import (
            ContentType,
            _generate_finding,
        )

        finding = _generate_finding(
            control_id="PR.AC-01",
            control_name="Identity and Credentials",
            function="PROTECT",
            category="Identity Management and Access Control",
            control_description="Manage user identities and credentials.",
            content_type=ContentType.DESIGN_DOC,
            relevance_score=0.8,
        )

        assert finding.control_id == "PR.AC-01"
        assert "design document" in finding.finding.lower()
        assert "PR.AC-01" in finding.rationale
        assert finding.severity in [Severity.HIGH, Severity.CRITICAL]

    @pytest.mark.asyncio
    async def test_generate_finding_code(self) -> None:
        """Test finding generation for code content type."""
        from compliance_oracle.tools.evaluation import (
            ContentType,
            _generate_finding,
        )

        finding = _generate_finding(
            control_id="PR.DS-01",
            control_name="Data Security",
            function="PROTECT",
            category="Data Security",
            control_description="Protect data at rest.",
            content_type=ContentType.CODE,
            relevance_score=0.75,
        )

        assert finding.control_id == "PR.DS-01"
        assert "code" in finding.finding.lower()

    @pytest.mark.asyncio
    async def test_generate_finding_no_fix_suggestions(self) -> None:
        """Test findings do not suggest fixes (core principle)."""
        from compliance_oracle.tools.evaluation import (
            ContentType,
            _generate_finding,
        )

        finding = _generate_finding(
            control_id="PR.AC-01",
            control_name="Identity and Credentials",
            function="PROTECT",
            category="Identity Management",
            control_description="Manage identities.",
            content_type=ContentType.DESIGN_DOC,
            relevance_score=0.8,
        )

        # Finding should describe gap, not solution
        assert "implement" not in finding.finding.lower()
        assert "should" not in finding.finding.lower()
        assert "must" not in finding.finding.lower()
        # Rationale explains the requirement, not how to fix
        assert "requires:" in finding.rationale


class TestNoFixPolicyIntegration:
    """Tests for no-fix policy integration with evaluation outputs."""

    def test_policy_guard_available_for_evaluation(self) -> None:
        """Policy guard is available for use with evaluation outputs."""
        from compliance_oracle.assessment.policy import enforce_no_fix_policy

        # Simulate evaluation output that should be checked
        evaluation_text = "No evidence found in design document addressing MFA"
        result = enforce_no_fix_policy(evaluation_text)

        assert result.policy_violation is False

    def test_policy_guard_catches_violations_in_findings(self) -> None:
        """Policy guard catches violations if present in finding text."""
        from compliance_oracle.assessment.policy import enforce_no_fix_policy

        # Simulate finding with accidentally included remediation language
        bad_finding = "No evidence found. You should implement MFA to fix this."
        result = enforce_no_fix_policy(bad_finding)

        assert result.policy_violation is True
        assert len(result.violations) >= 1

    def test_policy_guard_preserves_legitimate_finding_text(self) -> None:
        """Policy guard preserves legitimate finding text."""
        from compliance_oracle.assessment.policy import enforce_no_fix_policy

        legitimate_finding = (
            "No evidence found in design document addressing Identity and Credentials. "
            "CSF PR.AC-01 requires: Manage user identities and credentials using "
            "automated tools. The evaluated design document does not demonstrate "
            "coverage of this requirement."
        )
        result = enforce_no_fix_policy(legitimate_finding)

        assert result.policy_violation is False
        assert result.sanitized_text == legitimate_finding

    def test_finding_rationale_no_remediation_language(self) -> None:
        """Finding rationale should not contain remediation language."""
        from compliance_oracle.tools.evaluation import (
            ContentType,
            _generate_finding,
        )

        finding = _generate_finding(
            control_id="PR.DS-02",
            control_name="Data Security",
            function="PROTECT",
            category="Data Security",
            control_description="Protect data at rest.",
            content_type=ContentType.DESIGN_DOC,
            relevance_score=0.85,
        )

        # Rationale should not suggest fixes
        from compliance_oracle.assessment.policy import enforce_no_fix_policy
        result = enforce_no_fix_policy(finding.rationale)
        assert result.policy_violation is False, f"Rationale contains violations: {result.violations}"

    def test_compliant_area_text_no_remediation(self) -> None:
        """Compliant area text should not contain remediation language."""
        from compliance_oracle.assessment.policy import enforce_no_fix_policy
        from compliance_oracle.tools.evaluation import _find_compliant_areas

        content = "We use MFA for all users and encrypt data at rest."
        areas = _find_compliant_areas(content, content.lower())

        for area in areas:
            result = enforce_no_fix_policy(area)
            assert result.policy_violation is False, f"Compliant area contains violations: {result.violations}"
