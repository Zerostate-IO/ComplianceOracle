"""Tests for RAG search module (ControlSearcher class)."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from compliance_oracle.models.schemas import Control, ControlDetails
from compliance_oracle.rag.search import ControlSearcher

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_control_for_rag() -> Control:
    """Sample control for RAG testing."""
    return Control(
        id="PR.AC-01",
        name="Identity and Credentials",
        description="Manage user identities and credentials using automated tools.",
        framework_id="nist-csf-2.0",
        function_id="PR",
        function_name="PROTECT",
        category_id="PR.AC",
        category_name="Identity Management and Access Control",
        implementation_examples=[
            "Implement centralized identity management system",
            "Use MFA for privileged access",
        ],
        informative_references=["NIST SP 800-53: IA-1, IA-2", "ISO 27001: A.9.2"],
        keywords=["identity", "credentials", "access"],
    )


@pytest.fixture
def sample_control_minimal() -> Control:
    """Sample control with minimal fields."""
    return Control(
        id="PR.DS-01",
        name="Data Security",
        description="Protect data at rest.",
        framework_id="nist-csf-2.0",
        function_id="PR",
        function_name="PROTECT",
        category_id="PR.DS",
        category_name="Data Security",
        implementation_examples=[],
        informative_references=[],
        keywords=[],
    )


@pytest.fixture
def sample_control_details_for_rag(sample_control_for_rag: Control) -> ControlDetails:
    """Sample control details for RAG testing."""
    return ControlDetails(
        id=sample_control_for_rag.id,
        name=sample_control_for_rag.name,
        description=sample_control_for_rag.description,
        framework_id=sample_control_for_rag.framework_id,
        function_id=sample_control_for_rag.function_id,
        function_name=sample_control_for_rag.function_name,
        category_id=sample_control_for_rag.category_id,
        category_name=sample_control_for_rag.category_name,
        implementation_examples=sample_control_for_rag.implementation_examples,
        informative_references=sample_control_for_rag.informative_references,
        keywords=sample_control_for_rag.keywords,
        related_controls=["PR.AC-02"],
        mappings={"nist-800-53-r5": ["IA-1"]},
    )


@pytest.fixture
def mock_chroma_collection() -> MagicMock:
    """Mock ChromaDB collection."""
    collection = MagicMock()
    collection.upsert = MagicMock()
    collection.query = MagicMock(return_value={"ids": [], "metadatas": [], "distances": []})
    collection.get = MagicMock(return_value={"ids": [], "metadatas": []})
    collection.delete = MagicMock()
    collection.count = MagicMock(return_value=0)
    return collection


@pytest.fixture
def mock_chroma_client(mock_chroma_collection: MagicMock) -> MagicMock:
    """Mock ChromaDB client."""
    client = MagicMock()
    client.get_or_create_collection = MagicMock(return_value=mock_chroma_collection)
    client.delete_collection = MagicMock()
    return client


@pytest.fixture
def mock_framework_manager_for_rag(
    sample_control_for_rag: Control,
    sample_control_minimal: Control,
    sample_control_details_for_rag: ControlDetails,
) -> MagicMock:
    """Mock FrameworkManager for RAG testing."""
    manager = MagicMock()
    manager.list_controls = AsyncMock(return_value=[sample_control_for_rag, sample_control_minimal])
    manager.get_control_details = AsyncMock(return_value=sample_control_details_for_rag)
    return manager


# ============================================================================
# Test Initialization
# ============================================================================


class TestControlSearcherInit:
    """Tests for ControlSearcher initialization."""

    def test_init_with_default_path(self) -> None:
        """Test initialization with default db_path."""
        searcher = ControlSearcher()

        # Default path should be data/chroma relative to package
        assert "data" in str(searcher._db_path)
        assert "chroma" in str(searcher._db_path)
        assert searcher._client is None
        assert searcher._collection is None

    def test_init_with_custom_path(self, tmp_path: Path) -> None:
        """Test initialization with custom db_path."""
        custom_path = tmp_path / "custom_chroma"
        searcher = ControlSearcher(db_path=custom_path)

        assert searcher._db_path == custom_path
        assert searcher._client is None

    def test_init_with_custom_framework_manager(
        self, mock_framework_manager_for_rag: MagicMock
    ) -> None:
        """Test initialization with custom FrameworkManager."""
        searcher = ControlSearcher(framework_manager=mock_framework_manager_for_rag)

        assert searcher._framework_manager is mock_framework_manager_for_rag

    def test_init_creates_default_framework_manager(self) -> None:
        """Test that a default FrameworkManager is created if not provided."""
        searcher = ControlSearcher()

        assert searcher._framework_manager is not None


# ============================================================================
# Test _get_client
# ============================================================================


class TestGetClient:
    """Tests for _get_client method."""

    def test_get_client_creates_directory(self, tmp_path: Path) -> None:
        """Test that _get_client creates the db directory."""
        db_path = tmp_path / "new_chroma_dir"
        searcher = ControlSearcher(db_path=db_path)

        with patch("compliance_oracle.rag.search.chromadb.PersistentClient") as mock_client_cls:
            mock_client_cls.return_value = MagicMock()
            _ = searcher._get_client()

            assert db_path.exists()
            mock_client_cls.assert_called_once()

    def test_get_client_returns_cached_client(self, tmp_path: Path) -> None:
        """Test that _get_client returns cached client."""
        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch("compliance_oracle.rag.search.chromadb.PersistentClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client

            client1 = searcher._get_client()
            client2 = searcher._get_client()

            # Should only create client once
            mock_client_cls.assert_called_once()
            assert client1 is client2

    def test_get_client_uses_correct_settings(self, tmp_path: Path) -> None:
        """Test that _get_client uses correct ChromaDB settings."""
        db_path = tmp_path / "chroma"
        searcher = ControlSearcher(db_path=db_path)

        with patch("compliance_oracle.rag.search.chromadb.PersistentClient") as mock_client_cls, patch("compliance_oracle.rag.search.Settings") as mock_settings_cls:
            mock_client_cls.return_value = MagicMock()
            searcher._get_client()

            # Verify Settings was called with anonymized_telemetry=False
            mock_settings_cls.assert_called_once_with(anonymized_telemetry=False)


# ============================================================================
# Test _get_collection
# ============================================================================


class TestGetCollection:
    """Tests for _get_collection method."""

    def test_get_collection_creates_collection(self, tmp_path: Path) -> None:
        """Test that _get_collection creates collection with correct name."""
        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_client.get_or_create_collection = MagicMock(return_value=mock_collection)
            mock_get_client.return_value = mock_client

            _ = searcher._get_collection()

            mock_client.get_or_create_collection.assert_called_once()
            call_args = mock_client.get_or_create_collection.call_args
            assert call_args.kwargs["name"] == ControlSearcher.COLLECTION_NAME
            assert call_args.kwargs["metadata"] == {"hnsw:space": "cosine"}

    def test_get_collection_returns_cached_collection(self, tmp_path: Path) -> None:
        """Test that _get_collection returns cached collection."""
        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_client.get_or_create_collection = MagicMock(return_value=mock_collection)
            mock_get_client.return_value = mock_client

            collection1 = searcher._get_collection()
            collection2 = searcher._get_collection()

            # Should only create collection once
            mock_client.get_or_create_collection.assert_called_once()
            assert collection1 is collection2


# ============================================================================
# Test _build_document_text
# ============================================================================


class TestBuildDocumentText:
    """Tests for _build_document_text method."""

    def test_build_document_text_full(self, sample_control_for_rag: Control) -> None:
        """Test building document text with all fields."""
        searcher = ControlSearcher()
        doc_text = searcher._build_document_text(sample_control_for_rag)

        assert "Control: PR.AC-01 - Identity and Credentials" in doc_text
        assert "Description: Manage user identities" in doc_text
        assert "Function: PROTECT" in doc_text
        assert "Category: Identity Management and Access Control" in doc_text
        assert "Implementation Examples:" in doc_text
        assert "- Implement centralized identity management system" in doc_text
        assert "References:" in doc_text
        assert "- NIST SP 800-53: IA-1, IA-2" in doc_text
        assert "Keywords: identity, credentials, access" in doc_text

    def test_build_document_text_minimal(self, sample_control_minimal: Control) -> None:
        """Test building document text with minimal fields."""
        searcher = ControlSearcher()
        doc_text = searcher._build_document_text(sample_control_minimal)

        assert "Control: PR.DS-01 - Data Security" in doc_text
        assert "Description: Protect data at rest." in doc_text
        assert "Implementation Examples:" not in doc_text
        assert "References:" not in doc_text
        assert "Keywords:" not in doc_text

    def test_build_document_text_limited_references(self) -> None:
        """Test that references are limited to 5 items."""
        control = Control(
            id="TEST-01",
            name="Test Control",
            description="Test description",
            framework_id="test",
            function_id="T",
            function_name="TEST",
            category_id="T.C",
            category_name="Test Category",
            implementation_examples=[],
            informative_references=[f"Ref {i}" for i in range(10)],
            keywords=[],
        )
        searcher = ControlSearcher()
        doc_text = searcher._build_document_text(control)

        # Count reference lines
        ref_lines = [line for line in doc_text.split("\n") if line.startswith("- Ref")]
        assert len(ref_lines) == 5


# ============================================================================
# Test index_framework
# ============================================================================


class TestIndexFramework:
    """Tests for index_framework method."""

    @pytest.mark.asyncio
    async def test_index_framework_indexes_controls(
        self,
        mock_framework_manager_for_rag: MagicMock,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that index_framework indexes all controls."""
        searcher = ControlSearcher(
            db_path=tmp_path / "chroma",
            framework_manager=mock_framework_manager_for_rag,
        )

        # Mock _get_collection
        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            count = await searcher.index_framework("nist-csf-2.0")

        assert count == 2  # Two controls in mock
        mock_chroma_collection.upsert.assert_called_once()

        # Verify upsert was called with correct structure
        call_args = mock_chroma_collection.upsert.call_args
        assert len(call_args.kwargs["ids"]) == 2
        assert len(call_args.kwargs["documents"]) == 2
        assert len(call_args.kwargs["metadatas"]) == 2

    @pytest.mark.asyncio
    async def test_index_framework_returns_zero_for_no_controls(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that index_framework returns 0 when no controls."""
        mock_manager = MagicMock()
        mock_manager.list_controls = AsyncMock(return_value=[])

        searcher = ControlSearcher(
            db_path=tmp_path / "chroma",
            framework_manager=mock_manager,
        )

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            count = await searcher.index_framework("empty-framework")

        assert count == 0
        mock_chroma_collection.upsert.assert_not_called()

    @pytest.mark.asyncio
    async def test_index_framework_metadata_structure(
        self,
        mock_framework_manager_for_rag: MagicMock,
        mock_chroma_collection: MagicMock,
        sample_control_for_rag: Control,
        tmp_path: Path,
    ) -> None:
        """Test that metadata is structured correctly."""
        # Only return one control for easier testing
        mock_framework_manager_for_rag.list_controls = AsyncMock(
            return_value=[sample_control_for_rag]
        )

        searcher = ControlSearcher(
            db_path=tmp_path / "chroma",
            framework_manager=mock_framework_manager_for_rag,
        )

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            await searcher.index_framework("nist-csf-2.0")

        call_args = mock_chroma_collection.upsert.call_args
        metadata = call_args.kwargs["metadatas"][0]

        assert metadata["control_id"] == "PR.AC-01"
        assert metadata["control_name"] == "Identity and Credentials"
        assert metadata["framework_id"] == "nist-csf-2.0"
        assert metadata["function_id"] == "PR"
        assert metadata["function_name"] == "PROTECT"
        assert metadata["category_id"] == "PR.AC"
        assert metadata["category_name"] == "Identity Management and Access Control"
        assert "Manage user identities" in metadata["description"]


# ============================================================================
# Test search
# ============================================================================


class TestSearch:
    """Tests for search method."""

    @pytest.mark.asyncio
    async def test_search_returns_results(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test search returns formatted results."""
        mock_chroma_collection.query.return_value = {
            "ids": [["nist-csf-2.0:PR.AC-01"]],
            "metadatas": [
                [
                    {
                        "control_id": "PR.AC-01",
                        "control_name": "Identity and Credentials",
                        "description": "Manage identities",
                        "framework_id": "nist-csf-2.0",
                    }
                ]
            ],
            "distances": [[0.1]],
        }

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            results = await searcher.search(query="identity management")

        assert len(results) == 1
        assert results[0].control_id == "PR.AC-01"
        assert results[0].control_name == "Identity and Credentials"
        assert results[0].framework_id == "nist-csf-2.0"

    @pytest.mark.asyncio
    async def test_search_with_framework_filter(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test search with framework_id filter."""
        mock_chroma_collection.query.return_value = {
            "ids": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            await searcher.search(query="encryption", framework_id="nist-csf-2.0")

        call_args = mock_chroma_collection.query.call_args
        assert call_args.kwargs["where"] == {"framework_id": "nist-csf-2.0"}

    @pytest.mark.asyncio
    async def test_search_with_limit(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test search respects limit parameter."""
        mock_chroma_collection.query.return_value = {
            "ids": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            await searcher.search(query="test", limit=5)

        call_args = mock_chroma_collection.query.call_args
        assert call_args.kwargs["n_results"] == 5

    @pytest.mark.asyncio
    async def test_search_empty_results(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test search with no matches returns empty list."""
        mock_chroma_collection.query.return_value = {
            "ids": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            results = await searcher.search(query="nonexistent")

        assert results == []

    @pytest.mark.asyncio
    async def test_search_handles_none_ids(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test search handles None ids in response."""
        mock_chroma_collection.query.return_value = {
            "ids": None,
            "metadatas": None,
            "distances": None,
        }

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            results = await searcher.search(query="test")

        assert results == []

    @pytest.mark.asyncio
    async def test_search_handles_empty_first_id_list(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test search handles empty first id list."""
        mock_chroma_collection.query.return_value = {
            "ids": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            results = await searcher.search(query="test")

        assert results == []

    @pytest.mark.asyncio
    async def test_search_relevance_score_calculation(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that relevance score is calculated correctly from distance."""
        # Distance of 0.2 should give score of 1.0 - (0.2 / 2.0) = 0.9
        mock_chroma_collection.query.return_value = {
            "ids": [["test-01"]],
            "metadatas": [
                [
                    {
                        "control_id": "TEST-01",
                        "control_name": "Test",
                        "description": "Test",
                        "framework_id": "test",
                    }
                ]
            ],
            "distances": [[0.2]],
        }

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            results = await searcher.search(query="test")

        assert len(results) == 1
        # 1.0 - (0.2 / 2.0) = 0.9
        assert results[0].relevance_score == pytest.approx(0.9, rel=0.01)

    @pytest.mark.asyncio
    async def test_search_relevance_score_bounded(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that relevance score is bounded between 0 and 1."""
        # Distance of 3.0 would give negative score, should be bounded to 0
        mock_chroma_collection.query.return_value = {
            "ids": [["test-01"]],
            "metadatas": [
                [
                    {
                        "control_id": "TEST-01",
                        "control_name": "Test",
                        "description": "Test",
                        "framework_id": "test",
                    }
                ]
            ],
            "distances": [[3.0]],
        }

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            results = await searcher.search(query="test")

        assert results[0].relevance_score >= 0.0
        assert results[0].relevance_score <= 1.0

    @pytest.mark.asyncio
    async def test_search_handles_missing_metadata(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test search handles missing metadata gracefully."""
        # When metadatas[0] is an empty list, the code should handle it
        mock_chroma_collection.query.return_value = {
            "ids": [["test-01"]],
            "metadatas": [[]],  # Empty metadata list
            "distances": [[0.5]],
        }

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            results = await searcher.search(query="test")

        # Should still return a result with empty strings from metadata
        assert len(results) == 1
        assert results[0].control_id == ""
        assert results[0].control_name == ""

    @pytest.mark.asyncio
    async def test_search_handles_shorter_metadata_list(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test search handles when metadata list is shorter than ids."""
        mock_chroma_collection.query.return_value = {
            "ids": [["test-01", "test-02"]],
            "metadatas": [
                [
                    {
                        "control_id": "TEST-01",
                        "control_name": "Test 1",
                        "description": "",
                        "framework_id": "",
                    }
                ]
            ],  # Only one metadata
            "distances": [[0.5, 0.6]],
        }

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            results = await searcher.search(query="test")

        assert len(results) == 2


# ============================================================================
# Test get_context
# ============================================================================


class TestGetContext:
    """Tests for get_context method."""

    @pytest.mark.asyncio
    async def test_get_context_returns_full_context(
        self,
        mock_framework_manager_for_rag: MagicMock,
        mock_chroma_collection: MagicMock,
        sample_control_details_for_rag: ControlDetails,
        tmp_path: Path,
    ) -> None:
        """Test get_context returns full control context."""
        mock_chroma_collection.query.return_value = {
            "ids": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        searcher = ControlSearcher(
            db_path=tmp_path / "chroma",
            framework_manager=mock_framework_manager_for_rag,
        )

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            context = await searcher.get_context("PR.AC-01")

        assert "control" in context
        assert "hierarchy" in context
        assert context["hierarchy"]["framework_id"] == "nist-csf-2.0"
        assert context["hierarchy"]["function"]["id"] == "PR"

    @pytest.mark.asyncio
    async def test_get_context_includes_siblings(
        self,
        mock_framework_manager_for_rag: MagicMock,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test get_context includes sibling controls."""
        mock_chroma_collection.query.return_value = {
            "ids": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        searcher = ControlSearcher(
            db_path=tmp_path / "chroma",
            framework_manager=mock_framework_manager_for_rag,
        )

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            context = await searcher.get_context("PR.AC-01", include_siblings=True)

        assert "siblings" in context

    @pytest.mark.asyncio
    async def test_get_context_excludes_siblings(
        self,
        mock_framework_manager_for_rag: MagicMock,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test get_context excludes siblings when flag is False."""
        mock_chroma_collection.query.return_value = {
            "ids": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        searcher = ControlSearcher(
            db_path=tmp_path / "chroma",
            framework_manager=mock_framework_manager_for_rag,
        )

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            context = await searcher.get_context("PR.AC-01", include_siblings=False)

        assert "siblings" not in context

    @pytest.mark.asyncio
    async def test_get_context_includes_related(
        self,
        mock_framework_manager_for_rag: MagicMock,
        mock_chroma_collection: MagicMock,
        sample_control_details_for_rag: ControlDetails,
        tmp_path: Path,
    ) -> None:
        """Test get_context includes semantically related controls."""
        mock_chroma_collection.query.return_value = {
            "ids": [["nist-csf-2.0:PR.AC-02"]],
            "metadatas": [
                [
                    {
                        "control_id": "PR.AC-02",
                        "control_name": "Related Control",
                        "description": "Related",
                        "framework_id": "nist-csf-2.0",
                    }
                ]
            ],
            "distances": [[0.3]],
        }

        searcher = ControlSearcher(
            db_path=tmp_path / "chroma",
            framework_manager=mock_framework_manager_for_rag,
        )

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            context = await searcher.get_context("PR.AC-01", include_related=True)

        assert "related" in context

    @pytest.mark.asyncio
    async def test_get_context_excludes_related(
        self,
        mock_framework_manager_for_rag: MagicMock,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test get_context excludes related controls when flag is False."""
        mock_chroma_collection.query.return_value = {
            "ids": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        searcher = ControlSearcher(
            db_path=tmp_path / "chroma",
            framework_manager=mock_framework_manager_for_rag,
        )

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            context = await searcher.get_context("PR.AC-01", include_related=False)

        assert "related" not in context

    @pytest.mark.asyncio
    async def test_get_context_control_not_found(
        self,
        mock_chroma_collection: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test get_context returns error when control not found."""
        mock_manager = MagicMock()
        mock_manager.get_control_details = AsyncMock(return_value=None)

        searcher = ControlSearcher(
            db_path=tmp_path / "chroma",
            framework_manager=mock_manager,
        )

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            context = await searcher.get_context("INVALID-99")

        assert "error" in context
        assert "INVALID-99" in context["error"]

    @pytest.mark.asyncio
    async def test_get_context_filters_self_from_related(
        self,
        mock_framework_manager_for_rag: MagicMock,
        mock_chroma_collection: MagicMock,
        sample_control_details_for_rag: ControlDetails,
        tmp_path: Path,
    ) -> None:
        """Test get_context filters out the control itself from related results."""
        # Return the same control in search results
        mock_chroma_collection.query.return_value = {
            "ids": [["nist-csf-2.0:PR.AC-01"]],
            "metadatas": [
                [
                    {
                        "control_id": "PR.AC-01",
                        "control_name": "Identity and Credentials",
                        "description": "Same control",
                        "framework_id": "nist-csf-2.0",
                    }
                ]
            ],
            "distances": [[0.1]],
        }

        searcher = ControlSearcher(
            db_path=tmp_path / "chroma",
            framework_manager=mock_framework_manager_for_rag,
        )

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            context = await searcher.get_context("PR.AC-01", include_related=True)

        # The control itself should be filtered from related
        related_ids = [r["id"] for r in context.get("related", [])]
        assert "PR.AC-01" not in related_ids


# ============================================================================
# Test is_indexed
# ============================================================================


class TestIsIndexed:
    """Tests for is_indexed method."""

    @pytest.mark.asyncio
    async def test_is_indexed_returns_true(
        self, mock_chroma_collection: MagicMock, tmp_path: Path
    ) -> None:
        """Test is_indexed returns True when framework has controls."""
        mock_chroma_collection.get.return_value = {"ids": ["some-id"]}

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            result = await searcher.is_indexed("nist-csf-2.0")

        assert result is True
        mock_chroma_collection.get.assert_called_once_with(
            where={"framework_id": "nist-csf-2.0"},
            limit=1,
        )

    @pytest.mark.asyncio
    async def test_is_indexed_returns_false(
        self, mock_chroma_collection: MagicMock, tmp_path: Path
    ) -> None:
        """Test is_indexed returns False when framework has no controls."""
        mock_chroma_collection.get.return_value = {"ids": []}

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            result = await searcher.is_indexed("empty-framework")

        assert result is False


# ============================================================================
# Test get_indexed_count
# ============================================================================


class TestGetIndexedCount:
    """Tests for get_indexed_count method."""

    @pytest.mark.asyncio
    async def test_get_indexed_count_with_framework(
        self, mock_chroma_collection: MagicMock, tmp_path: Path
    ) -> None:
        """Test get_indexed_count with framework filter."""
        mock_chroma_collection.get.return_value = {"ids": ["id1", "id2", "id3"]}

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            count = await searcher.get_indexed_count("nist-csf-2.0")

        assert count == 3
        mock_chroma_collection.get.assert_called_once_with(where={"framework_id": "nist-csf-2.0"})

    @pytest.mark.asyncio
    async def test_get_indexed_count_without_framework(
        self, mock_chroma_collection: MagicMock, tmp_path: Path
    ) -> None:
        """Test get_indexed_count without framework filter."""
        mock_chroma_collection.count.return_value = 42

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            count = await searcher.get_indexed_count()

        assert count == 42
        mock_chroma_collection.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_indexed_count_empty_framework(
        self, mock_chroma_collection: MagicMock, tmp_path: Path
    ) -> None:
        """Test get_indexed_count with empty framework."""
        mock_chroma_collection.get.return_value = {"ids": None}

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            count = await searcher.get_indexed_count("empty-framework")

        assert count == 0


# ============================================================================
# Test clear_index
# ============================================================================


class TestClearIndex:
    """Tests for clear_index method."""

    @pytest.mark.asyncio
    async def test_clear_index_with_framework(
        self, mock_chroma_collection: MagicMock, tmp_path: Path
    ) -> None:
        """Test clear_index removes controls for specific framework."""
        mock_chroma_collection.get.return_value = {"ids": ["id1", "id2"]}

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            count = await searcher.clear_index("nist-csf-2.0")

        assert count == 2
        mock_chroma_collection.delete.assert_called_once_with(ids=["id1", "id2"])

    @pytest.mark.asyncio
    async def test_clear_index_with_framework_empty(
        self, mock_chroma_collection: MagicMock, tmp_path: Path
    ) -> None:
        """Test clear_index with framework that has no controls."""
        mock_chroma_collection.get.return_value = {"ids": []}

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            count = await searcher.clear_index("empty-framework")

        assert count == 0
        mock_chroma_collection.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_clear_index_all(
        self, mock_chroma_collection: MagicMock, mock_chroma_client: MagicMock, tmp_path: Path
    ) -> None:
        """Test clear_index removes all controls when no framework specified."""
        mock_chroma_collection.count.return_value = 100

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection), patch.object(searcher, "_get_client", return_value=mock_chroma_client):
            count = await searcher.clear_index()

        assert count == 100
        mock_chroma_client.delete_collection.assert_called_once_with(
            ControlSearcher.COLLECTION_NAME
        )
        assert searcher._collection is None

    @pytest.mark.asyncio
    async def test_clear_index_with_none_ids(
        self, mock_chroma_collection: MagicMock, tmp_path: Path
    ) -> None:
        """Test clear_index handles None ids in response."""
        mock_chroma_collection.get.return_value = {"ids": None}

        searcher = ControlSearcher(db_path=tmp_path / "chroma")

        with patch.object(searcher, "_get_collection", return_value=mock_chroma_collection):
            count = await searcher.clear_index("test-framework")

        assert count == 0
        mock_chroma_collection.delete.assert_not_called()
