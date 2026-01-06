"""Search tools using RAG for semantic search over frameworks."""

from fastmcp import FastMCP

from compliance_oracle.rag.search import ControlSearcher
from compliance_oracle.models.schemas import SearchResponse


def register_search_tools(mcp: FastMCP) -> None:
    """Register search tools with the MCP server."""

    @mcp.tool()
    async def search_controls(
        query: str,
        framework: str | None = None,
        limit: int = 10,
    ) -> SearchResponse:
        """Semantic search across compliance framework controls.

        Use this to find relevant controls for a given topic, requirement,
        or implementation question.

        Args:
            query: Natural language search query (e.g., 'encryption at rest',
                   'multi-factor authentication', 'incident response')
            framework: Limit search to specific framework (optional)
            limit: Maximum number of results (default: 10)

        Returns:
            List of relevant controls with relevance scores.

        Examples:
            - "controls about encryption" -> PR.DS-01, PR.DS-02, etc.
            - "access control requirements" -> PR.AC-01 through PR.AC-06
            - "logging and monitoring" -> DE.CM-01, DE.AE-02, etc.
        """
        searcher = ControlSearcher()
        results = await searcher.search(
            query=query,
            framework_id=framework,
            limit=limit,
        )
        return SearchResponse(
            query=query,
            framework=framework,
            results=results,
            total_results=len(results),
        )

    @mcp.tool()
    async def get_control_context(
        control_id: str,
        framework: str = "nist-csf-2.0",
        include_siblings: bool = True,
        include_related: bool = True,
    ) -> dict:
        """Get full context for a control including hierarchy and relationships.

        Args:
            control_id: Control identifier (e.g., 'PR.DS-01')
            framework: Framework ID (default: 'nist-csf-2.0')
            include_siblings: Include other controls in same category
            include_related: Include semantically related controls

        Returns:
            Control context including:
            - The control itself
            - Parent function and category
            - Sibling controls (if requested)
            - Related controls (if requested)
        """
        searcher = ControlSearcher()
        return await searcher.get_context(
            control_id=control_id,
            framework_id=framework,
            include_siblings=include_siblings,
            include_related=include_related,
        )
