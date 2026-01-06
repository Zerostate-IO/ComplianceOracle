"""RAG-based semantic search for compliance controls using ChromaDB."""

from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.models.schemas import Control, SearchResult


class ControlSearcher:
    """Semantic search over compliance controls using ChromaDB.

    Uses sentence-transformers embeddings for semantic similarity search
    across control descriptions, implementation examples, and references.
    """

    COLLECTION_NAME = "compliance_controls"

    def __init__(
        self,
        db_path: Path | None = None,
        framework_manager: FrameworkManager | None = None,
    ) -> None:
        """Initialize the control searcher.

        Args:
            db_path: Path to ChromaDB persistence directory.
                     Defaults to data/chroma/ relative to package.
            framework_manager: Optional FrameworkManager instance.
        """
        if db_path is None:
            self._db_path = Path(__file__).parent.parent.parent.parent / "data" / "chroma"
        else:
            self._db_path = db_path

        self._framework_manager = framework_manager or FrameworkManager()
        self._client: chromadb.PersistentClient | None = None
        self._collection: chromadb.Collection | None = None

    def _get_client(self) -> chromadb.PersistentClient:
        """Get or create ChromaDB client."""
        if self._client is None:
            self._db_path.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(self._db_path),
                settings=Settings(anonymized_telemetry=False),
            )
        return self._client

    def _get_collection(self) -> chromadb.Collection:
        """Get or create the controls collection."""
        if self._collection is None:
            client = self._get_client()
            # Use default embedding function (sentence-transformers)
            self._collection = client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    async def index_framework(self, framework_id: str) -> int:
        """Index all controls from a framework into ChromaDB.

        Args:
            framework_id: Framework identifier to index.

        Returns:
            Number of controls indexed.
        """
        controls = await self._framework_manager.list_controls(framework_id)
        if not controls:
            return 0

        collection = self._get_collection()

        # Prepare documents for indexing
        ids = []
        documents = []
        metadatas = []

        for ctrl in controls:
            doc_id = f"{framework_id}:{ctrl.id}"

            # Build rich document text for embedding
            doc_text = self._build_document_text(ctrl)

            ids.append(doc_id)
            documents.append(doc_text)
            metadatas.append(
                {
                    "control_id": ctrl.id,
                    "control_name": ctrl.name,
                    "framework_id": framework_id,
                    "function_id": ctrl.function_id,
                    "function_name": ctrl.function_name,
                    "category_id": ctrl.category_id,
                    "category_name": ctrl.category_name,
                    "description": ctrl.description,
                }
            )

        # Add to collection (upserts if already exists)
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        return len(controls)

    def _build_document_text(self, ctrl: Control) -> str:
        """Build searchable document text from control."""
        parts = [
            f"Control: {ctrl.id} - {ctrl.name}",
            f"Description: {ctrl.description}",
            f"Function: {ctrl.function_name}",
            f"Category: {ctrl.category_name}",
        ]

        if ctrl.implementation_examples:
            parts.append("Implementation Examples:")
            for example in ctrl.implementation_examples:
                parts.append(f"- {example}")

        if ctrl.informative_references:
            parts.append("References:")
            for ref in ctrl.informative_references[:5]:  # Limit references
                parts.append(f"- {ref}")

        if ctrl.keywords:
            parts.append(f"Keywords: {', '.join(ctrl.keywords)}")

        return "\n".join(parts)

    async def search(
        self,
        query: str,
        framework_id: str | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Semantic search for controls matching a query.

        Args:
            query: Natural language search query.
            framework_id: Limit search to specific framework (optional).
            limit: Maximum number of results.

        Returns:
            List of search results with relevance scores.
        """
        collection = self._get_collection()

        # Build where clause for filtering
        where_clause = None
        if framework_id:
            where_clause = {"framework_id": framework_id}

        # Query the collection
        results = collection.query(
            query_texts=[query],
            n_results=limit,
            where=where_clause,
            include=["metadatas", "distances"],
        )

        # Convert to SearchResult objects
        search_results = []

        if results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            distances = results["distances"][0] if results["distances"] else []

            for i, doc_id in enumerate(ids):
                metadata = metadatas[i] if i < len(metadatas) else {}
                distance = distances[i] if i < len(distances) else 1.0

                # Convert cosine distance to similarity score (0-1)
                # Cosine distance ranges from 0 (identical) to 2 (opposite)
                relevance_score = max(0.0, min(1.0, 1.0 - (distance / 2.0)))

                search_results.append(
                    SearchResult(
                        control_id=metadata.get("control_id", ""),
                        control_name=metadata.get("control_name", ""),
                        description=metadata.get("description", ""),
                        framework_id=metadata.get("framework_id", ""),
                        relevance_score=relevance_score,
                    )
                )

        return search_results

    async def get_context(
        self,
        control_id: str,
        framework_id: str = "nist-csf-2.0",
        include_siblings: bool = True,
        include_related: bool = True,
    ) -> dict[str, Any]:
        """Get full context for a control including hierarchy and relationships.

        Args:
            control_id: Control identifier.
            framework_id: Framework identifier.
            include_siblings: Include other controls in same category.
            include_related: Include semantically related controls.

        Returns:
            Control context dictionary.
        """
        # Get the control details
        control = await self._framework_manager.get_control_details(
            framework_id=framework_id,
            control_id=control_id,
        )

        if not control:
            return {"error": f"Control {control_id} not found in {framework_id}"}

        context: dict[str, Any] = {
            "control": control.model_dump(),
            "hierarchy": {
                "framework_id": framework_id,
                "function": {
                    "id": control.function_id,
                    "name": control.function_name,
                },
                "category": {
                    "id": control.category_id,
                    "name": control.category_name,
                },
            },
        }

        # Get sibling controls (same category)
        if include_siblings:
            siblings = await self._framework_manager.list_controls(
                framework_id=framework_id,
                category_id=control.category_id,
            )
            context["siblings"] = [
                {"id": s.id, "name": s.name} for s in siblings if s.id != control_id
            ]

        # Get semantically related controls
        if include_related:
            # Search for similar controls using the control's description
            similar = await self.search(
                query=control.description,
                framework_id=framework_id,
                limit=6,  # Get a few extra since we'll filter out the control itself
            )
            context["related"] = [
                {"id": r.control_id, "name": r.control_name, "score": r.relevance_score}
                for r in similar
                if r.control_id != control_id
            ][:5]

        return context

    async def is_indexed(self, framework_id: str) -> bool:
        """Check if a framework has been indexed.

        Args:
            framework_id: Framework identifier.

        Returns:
            True if the framework has indexed controls.
        """
        collection = self._get_collection()

        # Check if any documents exist for this framework
        results = collection.get(
            where={"framework_id": framework_id},
            limit=1,
        )

        return bool(results["ids"])

    async def get_indexed_count(self, framework_id: str | None = None) -> int:
        """Get count of indexed controls.

        Args:
            framework_id: Filter by framework (optional).

        Returns:
            Number of indexed controls.
        """
        collection = self._get_collection()

        if framework_id:
            results = collection.get(
                where={"framework_id": framework_id},
            )
            return len(results["ids"]) if results["ids"] else 0
        else:
            return collection.count()

    async def clear_index(self, framework_id: str | None = None) -> int:
        """Clear indexed controls.

        Args:
            framework_id: Clear only this framework (optional).
                          If None, clears all controls.

        Returns:
            Number of controls removed.
        """
        collection = self._get_collection()

        if framework_id:
            # Get IDs to delete
            results = collection.get(
                where={"framework_id": framework_id},
            )
            if results["ids"]:
                collection.delete(ids=results["ids"])
                return len(results["ids"])
            return 0
        else:
            # Clear entire collection
            count = collection.count()
            client = self._get_client()
            client.delete_collection(self.COLLECTION_NAME)
            self._collection = None
            return count
