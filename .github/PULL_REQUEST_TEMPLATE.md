## What does this PR do?

<!-- Brief summary of the change and why. -->

## Related issue

<!-- Link the issue this closes, e.g. "Closes #12". -->

## Type of change

- [ ] Bug fix
- [ ] New feature / behavior change
- [ ] Docs
- [ ] Tests / eval
- [ ] Build / CI

## Checklist

- [ ] `uv run ruff check .` passes
- [ ] `uv run ruff format --check .` passes
- [ ] `uv run pyright` passes
- [ ] `uv run pytest` passes
- [ ] Added/adjusted tests for the change
- [ ] Followed [CONTRIBUTING.md](https://github.com/nathan-hoche/RepoSniffer/blob/main/CONTRIBUTING.md) conventions
      (conventional commit, minimal deps, no unnecessary comments, cache
      versioning bumped if candidate/embedding logic changed)

## Retrieval behavior changed?

If you touched `engine/` (query building, embedding, scoring, candidates), report
the eval numbers before/after (see the eval harness in CONTRIBUTING.md):

- hit@1: before `_` / after `_`
- hit@3: before `_` / after `_`
- hit@5: before `_` / after `_`

## Testing notes

<!-- How did you verify this? Offline tests only, or live against GitHub? -->