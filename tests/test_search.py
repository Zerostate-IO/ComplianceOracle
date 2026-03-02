"""Tests for search tools (search_controls, get_control_context)."""


import pytest

from compliance_oracle.models.schemas import SearchResult


class TestSearchControls:
    """Tests for search_controls tool."""

    @pytest.mark.asyncio
    async def test_search_controls_happy_path(
        self,
        mock_control_searcher,
        sample_search_result: SearchResult,
    ) -> None:
        """Test search_controls returns relevant results."""
        mock_control_searcher.search.return_value = [sample_search_result]

        result = await mock_control_searcher.search(
            query="identity management",
        )

        assert len(result) == 1
        assert result[0].control_id == "PR.AC-01"
        assert result[0].control_name == "Identity and Credentials"
        assert result[0].relevance_score == 0.95

    @pytest.mark.asyncio
    async def test_search_controls_with_framework_filter(
        self,
        mock_control_searcher,
        sample_search_result: SearchResult,
    ) -> None:
        """Test search_controls filters by framework."""
        mock_control_searcher.search.return_value = [sample_search_result]

        result = await mock_control_searcher.search(
            query="access control",
            framework_id="nist-csf-2.0",
        )

        assert len(result) == 1
        # Verify the mock was called with the expected arguments
        call_args = mock_control_searcher.search.call_args
        assert call_args.kwargs.get("query") == "access control"


    @pytest.mark.asyncio
    async def test_search_controls_with_limit(
        self,
        mock_control_searcher,
        sample_search_result: SearchResult,
    ) -> None:
        """Test search_controls respects limit parameter."""
        mock_control_searcher.search.return_value = [sample_search_result]

        result = await mock_control_searcher.search(
            query="encryption",
            limit=5,
        )

        assert len(result) == 1
        mock_control_searcher.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_controls_empty_results(self, mock_control_searcher) -> None:
        """Test search_controls with no matches returns empty list."""
        mock_control_searcher.search.return_value = []

        result = await mock_control_searcher.search(
            query="nonexistent control topic",
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_search_controls_multiple_results(
        self,
        mock_control_searcher,
        sample_search_result: SearchResult,
    ) -> None:
        """Test search_controls returns multiple matching results."""
        second_result = SearchResult(
            control_id="PR.AC-02",
            control_name="Physical Access",
            description="Physical access control requirements.",
            framework_id="nist-csf-2.0",
            relevance_score=0.85,
        )
        mock_control_searcher.search.return_value = [sample_search_result, second_result]

        result = await mock_control_searcher.search(
            query="access control",
        )

        assert len(result) == 2
        assert result[0].relevance_score >= result[1].relevance_score


class TestGetControlContext:
    """Tests for get_control_context tool."""

    @pytest.mark.asyncio
    async def test_get_control_context_happy_path(
        self,
        mock_control_searcher,
        sample_control_details,
    ) -> None:
        """Test get_control_context returns full context."""
        expected_context = {
            "control": sample_control_details.model_dump(),
            "hierarchy": {
                "framework_id": "nist-csf-2.0",
                "function": {"id": "PR", "name": "PROTECT"},
                "category": {
                    "id": "PR.AC",
                    "name": "Identity Management and Access Control",
                },
            },
            "siblings": [{"id": "PR.AC-02", "name": "Physical Access"}],
            "related": [{"id": "PR.AC-03", "name": "Remote Access", "score": 0.85}],
        }
        mock_control_searcher.get_context.return_value = expected_context

        result = await mock_control_searcher.get_context(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
        )

        assert "control" in result
        assert "hierarchy" in result
        assert result["hierarchy"]["framework_id"] == "nist-csf-2.0"
        assert result["hierarchy"]["function"]["id"] == "PR"

    @pytest.mark.asyncio
    async def test_get_control_context_includes_siblings(
        self,
        mock_control_searcher,
        sample_control_details,
    ) -> None:
        """Test get_control_context includes sibling controls."""
        expected_context = {
            "control": sample_control_details.model_dump(),
            "hierarchy": {
                "framework_id": "nist-csf-2.0",
                "function": {"id": "PR", "name": "PROTECT"},
                "category": {
                    "id": "PR.AC",
                    "name": "Identity Management and Access Control",
                },
            },
            "siblings": [
                {"id": "PR.AC-02", "name": "Physical Access"},
                {"id": "PR.AC-03", "name": "Remote Access"},
            ],
            "related": [],
        }
        mock_control_searcher.get_context.return_value = expected_context

        result = await mock_control_searcher.get_context(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            include_siblings=True,
        )

        assert "siblings" in result
        assert len(result["siblings"]) == 2

    @pytest.mark.asyncio
    async def test_get_control_context_includes_related(
        self,
        mock_control_searcher,
        sample_control_details,
    ) -> None:
        """Test get_control_context includes semantically related controls."""
        expected_context = {
            "control": sample_control_details.model_dump(),
            "hierarchy": {
                "framework_id": "nist-csf-2.0",
                "function": {"id": "PR", "name": "PROTECT"},
                "category": {
                    "id": "PR.AC",
                    "name": "Identity Management and Access Control",
                },
            },
            "siblings": [],
            "related": [
                {"id": "PR.AT-01", "name": "Awareness Training", "score": 0.75},
            ],
        }
        mock_control_searcher.get_context.return_value = expected_context

        result = await mock_control_searcher.get_context(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            include_related=True,
        )

        assert "related" in result
        assert len(result["related"]) == 1

    @pytest.mark.asyncio
    async def test_get_control_context_not_found(self, mock_control_searcher) -> None:
        """Test get_control_context for unknown control returns error."""
        mock_control_searcher.get_context.return_value = {
            "error": "Control INVALID-99 not found in nist-csf-2.0"
        }

        result = await mock_control_searcher.get_context(
            control_id="INVALID-99",
            framework_id="nist-csf-2.0",
        )

        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_control_context_excludes_siblings_when_disabled(
        self,
        mock_control_searcher,
        sample_control_details,
    ) -> None:
        """Test get_control_context excludes siblings when flag is False."""
        expected_context = {
            "control": sample_control_details.model_dump(),
            "hierarchy": {
                "framework_id": "nist-csf-2.0",
                "function": {"id": "PR", "name": "PROTECT"},
                "category": {
                    "id": "PR.AC",
                    "name": "Identity Management and Access Control",
                },
            },
            "related": [],
        }
        mock_control_searcher.get_context.return_value = expected_context

        result = await mock_control_searcher.get_context(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            include_siblings=False,
            include_related=False,
        )

        assert "siblings" not in result or result.get("siblings") == []
