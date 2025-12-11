import os
from collections import defaultdict
from urllib.parse import urlparse

from agents import function_tool
from bs4 import BeautifulSoup
from firecrawl import AsyncFirecrawl
from firecrawl.v2.types import ScrapeFormats


async def get_sitemap_urls_from_sitemap_index(sitemap_url: str) -> list[str]:
    """Fetch the sitemap URLs from a sitemap index file

    You can use this tool to fetch the sitemap URLs from a sitemap index file.
    """
    firecrawl_client = AsyncFirecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
    result = await firecrawl_client.scrape(
        sitemap_url, formats=ScrapeFormats(raw_html=True)
    )
    soup = BeautifulSoup(result.raw_html, "lxml")

    return [loc.text.strip() for loc in soup.find_all("loc")]


async def fetch_sitemap_urls_from_robots_txt(url: str) -> list[str]:
    """Fetch the sitemap URLs from a robots.txt file

    You can use this tool to determine where the relevant sitemap.xml is located.
    """
    firecrawl_client = AsyncFirecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
    print(f"{url}/robots.txt")
    result = await firecrawl_client.scrape(
        f"{url}/robots.txt", formats=ScrapeFormats(markdown=True)
    )
    sitemap_urls = list(
        set(
            [
                line.split("Sitemap:")[1].strip()
                for line in result.markdown.splitlines()
                if line.strip().startswith("Sitemap:")
            ]
        )
    )

    # Check each sitemap URL to see if it's a sitemap index or regular sitemap
    final_urls = []
    for sitemap_url in sitemap_urls:
        # Fetch the sitemap to check its structure
        sitemap_result = await firecrawl_client.scrape(
            sitemap_url, formats=ScrapeFormats(raw_html=True)
        )
        soup = BeautifulSoup(sitemap_result.raw_html, "lxml")
        # Check if it's a sitemap index (has <sitemapindex> tag)
        sitemapindex = soup.find("sitemapindex")
        if sitemapindex:
            # It's a sitemap index, extract all sitemap URLs
            sitemap_tags = soup.find_all("sitemap")
            for sitemap in sitemap_tags:
                loc = sitemap.find("loc")
                if loc and loc.text:
                    final_urls.append(loc.text.strip())
        else:
            # It's a regular sitemap (has <urlset> tag), return the URL itself
            final_urls.append(sitemap_url)

    return final_urls


@function_tool
async def fetch_urls_at_heirarchy_level_from_sitemap(
    sitemap_url: str,
    level: int,
    paths_to_ignore: list[str] | None = None,
) -> list[str]:
    """Fetch the URLs at a given hierarchy level from a sitemap.

    Args:
        sitemap_url: The URL of the sitemap XML file.
        level: The hierarchy level to fetch the URLs from (0 = root, 1 = first level, etc.).
        paths_to_ignore: Optional list of path patterns to ignore.

    Returns:
        A list of URLs found at the given hierarchy level.
    """
    urls = await fetch_sitemap(sitemap_url)

    result = get_unique_urls_by_hierarchy(
        get_root_url(sitemap_url), urls, paths_to_ignore=paths_to_ignore, level=level
    )
    # When level is provided, the function always returns a list
    assert isinstance(result, list), "Expected list when level is provided"
    return result  # type: ignore[return-value]


async def fetch_sitemap(url: str) -> list[str]:
    """Fetch a sitemap from a URL and extract all <loc> values.

    Args:
        url: The URL of the sitemap XML file.

    Returns:
        A list of URLs found in the <loc> elements of the sitemap.
    """
    # Fetch the sitemap XML
    firecrawl_client = AsyncFirecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
    result = await firecrawl_client.scrape(url, formats=ScrapeFormats(raw_html=True))
    soup = BeautifulSoup(result.raw_html, "lxml")
    urls = []

    # Check if it's a sitemap index (contains <sitemap> elements)
    sitemap_tags = soup.find_all("sitemap")
    if sitemap_tags:
        # Extract <loc> from <sitemap><loc>...</loc></sitemap>
        for sitemap in sitemap_tags:
            loc = sitemap.find("loc")
            if loc and loc.text:
                urls.append(loc.text.strip())
    else:
        # Regular sitemap (contains <url> elements)
        url_tags = soup.find_all("url")
        for url_elem in url_tags:
            loc = url_elem.find("loc")
            if loc and loc.text:
                urls.append(loc.text.strip())

    return urls


def get_root_url(url: str) -> str:
    """Get the root URL from a given URL."""
    root_parsed = urlparse(url)
    root_scheme = root_parsed.scheme
    root_netloc = root_parsed.netloc
    return f"{root_scheme}://{root_netloc}"


def get_unique_urls_by_hierarchy(
    root_url: str,
    urls: list[str],
    paths_to_ignore: list[str] | None = None,
    level: int | None = None,
) -> dict[int, list[str]] | list[str]:
    """Group unique URLs by their hierarchical level from the root URL.

    Args:
        root_url: The root URL to use as the base for hierarchy calculation.
        urls: A list of URLs to analyze.
        paths_to_ignore: Optional list of path patterns to ignore. URLs whose paths start with
            or exactly match any pattern in this list will be excluded. Patterns should be
            relative paths (e.g., "/admin/", "/api/v1/", "/private").
        level: Optional specific hierarchy level to return. If provided, returns only URLs
            at that level as a list. If None, returns a dictionary mapping all levels to URLs.

    Returns:
        If level is None: A dictionary mapping hierarchical levels (0, 1, 2, ...) to lists of unique URLs
        at that level. Level 0 is the root URL itself, level 1 is one path segment deep, etc.
        Example: {
            0: ["https://example.com/"],
            1: ["https://example.com/docs/", "https://example.com/blog/"],
            2: ["https://example.com/docs/api/", "https://example.com/blog/post1/"]
        }
        If level is specified: A list of URLs at that specific level.
        Example: ["https://example.com/docs/", "https://example.com/blog/"]
    """
    if paths_to_ignore is None:
        paths_to_ignore = []

    # Normalize ignore paths (ensure they start with / and end with / for prefix matching)
    normalized_ignore_paths = []
    for path in paths_to_ignore:
        # Normalize: ensure starts with /, and add / at end for prefix matching
        normalized = path.strip()
        if not normalized.startswith("/"):
            normalized = "/" + normalized
        # For prefix matching, we'll check if URL path starts with the pattern
        normalized_ignore_paths.append(normalized)
    # Parse the root URL
    root_parsed = urlparse(root_url)
    root_scheme = root_parsed.scheme
    root_netloc = root_parsed.netloc
    root_path = root_parsed.path.rstrip("/") or ""
    root_base = f"{root_scheme}://{root_netloc}"

    # Dictionary to store URLs by level
    urls_by_level: dict[int, set[str]] = defaultdict(set)

    # Normalize and add root URL at level 0
    root_normalized = f"{root_base}{root_path}/" if root_path else f"{root_base}/"
    urls_by_level[0].add(root_normalized)

    # Get root path segments for comparison
    root_segments = [seg for seg in root_path.split("/") if seg] if root_path else []

    for url in urls:
        try:
            parsed = urlparse(url)
            # Only process URLs from the same domain
            if parsed.scheme != root_scheme or parsed.netloc != root_netloc:
                continue

            # Get the path and split into segments
            url_path = parsed.path.rstrip("/") or ""
            path_segments = [seg for seg in url_path.split("/") if seg]

            # Check if this path should be ignored
            if normalized_ignore_paths:
                # Reconstruct the full path for comparison
                full_path = "/" + "/".join(path_segments) if path_segments else "/"

                should_ignore = False
                for ignore_path in normalized_ignore_paths:
                    # Check if path starts with ignore pattern (prefix match)
                    # or is an exact match (handling trailing slashes)
                    if full_path.startswith(
                        ignore_path
                    ) or full_path == ignore_path.rstrip("/"):
                        should_ignore = True
                        break

                if should_ignore:
                    continue

            # If root has a path, ensure URL starts with it
            if root_segments:
                if not path_segments[: len(root_segments)] == root_segments:
                    continue
                # Calculate level relative to root path
                url_level = len(path_segments) - len(root_segments)
            else:
                # Root is at domain level, count all segments
                url_level = len(path_segments)

            # Skip if level is negative (shouldn't happen, but safety check)
            if url_level < 0:
                continue

            # Normalize the URL (reconstruct from base + segments)
            if path_segments:
                normalized_url = f"{root_base}/{'/'.join(path_segments)}/"
            else:
                normalized_url = f"{root_base}/"

            urls_by_level[url_level].add(normalized_url)

        except Exception:
            # Skip invalid URLs
            continue

    # Convert sets to sorted lists for consistent output
    result = {
        hier_level: sorted(url_set)
        for hier_level, url_set in sorted(urls_by_level.items())
    }

    # If a specific level was requested, return only that level's URLs
    if level is not None:
        return result.get(level, [])

    return result


@function_tool
async def list_links_on_page(url: str) -> list[str]:
    """Use the firecrawl API to list all links on a page.

    You can use this tool to list all links on a page. This is useful to ensure you cover all pages of the application.

    Args:
        url: The URL of the page to list the links of.
    Returns:
        A list of URLs on the page. Example: ["https://www.google.com", "https://www.bing.com"]
    """
    firecrawl_client = AsyncFirecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
    result = await firecrawl_client.scrape(
        url, formats=ScrapeFormats(markdown=True, links=True)
    )
    return result.links


@function_tool
async def get_page_content_as_markdown(url: str) -> list[str]:
    """Use the firecrawl API to fetch the page content as markdown.

    You can use this tool to fetch the page content as markdown. This is useful to get the content in a format easier to parse by the agent.

    Args:
        url: The URL of the page to list the links of.
    Returns:
        The content of the page as markdown. Example: "# Audit Logs API"
    """
    firecrawl_client = AsyncFirecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
    result = await firecrawl_client.scrape(url, formats=ScrapeFormats(markdown=True))
    return result.markdown
