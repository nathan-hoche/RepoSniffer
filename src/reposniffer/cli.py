from __future__ import annotations

import json
import sys
from typing import NoReturn

import typer
from rich.console import Console
from rich.table import Table

from reposniffer.config import Settings
from reposniffer.engine.github import GitHubError, RateLimitError
from reposniffer.engine.search import build_engine

app = typer.Typer(
    add_completion=False,
    help="RepoSniffer: find the best open-source project for a described feature.",
)
console = Console()


def _handle_error(exc: GitHubError) -> NoReturn:
    if isinstance(exc, RateLimitError):
        hint = (
            "set GITHUB_TOKEN to raise the limit" if not Settings().github_token else "retry later"
        )
        console.print(f"[red]GitHub rate limit hit — {hint}.[/red]")
    else:
        console.print(f"[red]{exc}[/red]")
    raise typer.Exit(code=1)


def _warn_no_token() -> None:
    if not Settings().github_token:
        console.print(
            "[yellow]No GITHUB_TOKEN set — unauthenticated GitHub limits are low "
            "(60 req/hr) and one query can exhaust them. Create a token at "
            "https://github.com/settings/tokens and export GITHUB_TOKEN=ghp_... "
            "for reliable results.[/yellow]"
        )


@app.command()
def search(
    query: str = typer.Argument(..., help="Plain-language feature description."),
    intent: str = typer.Option("adopt", "--intent", "-i", help="adopt or study"),
    language: str | None = typer.Option(None, "--language", "-l", help="Filter by language."),
    license_key: str | None = typer.Option(None, "--license", help="Filter by SPDX license key."),
    min_stars: int | None = typer.Option(None, "--min-stars", help="Minimum stars."),
    top_k: int = typer.Option(5, "--top-k", min=1, max=20),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON instead of a table."),
) -> None:
    _warn_no_token()
    engine = build_engine(Settings())
    try:
        results = engine.search(
            query=query,
            language=language,
            license_key=license_key,
            min_stars=min_stars,
            intent=intent,  # type: ignore[arg-type]
            top_k=top_k,
        )
    except GitHubError as exc:
        _handle_error(exc)
    finally:
        engine.close()
    if json_out:
        sys.stdout.write(
            json.dumps(
                {
                    "query": query,
                    "intent": intent,
                    "as_of": results[0]["as_of"] if results else None,
                    "results": results,
                },
                indent=2,
            )
            + "\n"
        )
        return
    table = Table(title=f"RepoSniffer — {query!r} ({intent})")
    for col in ("#", "Repo", "Stars", "Lang", "License", "Activity", "Overall", "Recommendation"):
        table.add_column(col)
    for r in results:
        table.add_row(
            str(r["rank"]),
            r["full_name"],
            str(r["stars"]),
            str(r["language"] or ""),
            str(r["license"] or "none"),
            f"{r['activity']:.2f}",
            f"{r['overall']:.3f}",
            r["recommendation"],
        )
    console.print(table)


@app.command()
def intel(
    owner_repo: str = typer.Argument(..., help="owner/repo to verify."),
    query: str | None = typer.Option(None, "--query", "-q", help="Optional framing query."),
    top_k: int = typer.Option(2, "--top-k"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    _warn_no_token()
    engine = build_engine(Settings())
    try:
        result = engine.repo_intel(owner_repo=owner_repo, query=query, top_k=top_k)
    except GitHubError as exc:
        _handle_error(exc)
    finally:
        engine.close()
    if json_out:
        sys.stdout.write(json.dumps(result, indent=2) + "\n")
        return
    console.print(f"[bold]{result['full_name']}[/bold] — {result['status']}")
    console.print(
        f"  {result['html_url']} | stars={result['stars']} forks={result['forks']} lang={result['language']} license={result['license']}"
    )
    if result.get("alternatives"):
        console.print("  alternatives:")
        for alt in result["alternatives"]:
            console.print(f"    {alt['rank']}. {alt['full_name']} — {alt['recommendation']}")


@app.command()
def doctor() -> None:
    """Check embedding backend, model, and GitHub auth."""
    settings = Settings()
    for k, v in settings.summary().items():
        console.print(f"{k}: {v}")
    engine = build_engine(settings)
    try:
        console.print(f"embedding model: {engine.model_name}")
    finally:
        engine.close()


if __name__ == "__main__":
    app()
