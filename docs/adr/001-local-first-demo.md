# ADR 001: local-first demo adapter

## Context

The assignment asks for one marketplace port with a simulator adapter and a live Upwork adapter. Reviewers need a safe mode that does not require OAuth or browser automation.

## Decision

The default `demo` mode reads synthetic jobs from the repository and writes only local proposal drafts. A separate `UpworkLiveAdapter` is an explicit, unconfigured boundary that raises a clear setup error until OAuth credentials and approved MCP connectivity are supplied.

## Consequences

The submission can be tested end to end locally. It intentionally does not claim live Upwork support has been exercised.

