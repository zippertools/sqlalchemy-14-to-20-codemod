from __future__ import annotations

import html
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, cast

from actions_upgrade_guard.models import ScanReport


def _normalize(value: Any) -> Any:
    if is_dataclass(value):
        data = asdict(cast(Any, value))
        dataclass_value = cast(Any, value)
        if hasattr(dataclass_value, "status"):
            data["status"] = dataclass_value.status
        if hasattr(dataclass_value, "blocking_findings"):
            data["blocking_findings"] = len(dataclass_value.blocking_findings)
        return _normalize(data)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


def report_to_json(report: ScanReport) -> str:
    return json.dumps(_normalize(report), indent=2, sort_keys=True)


def _badge(value: str) -> str:
    safe = html.escape(value)
    return f'<span class="badge badge-{safe}">{safe}</span>'


def report_to_html(report: ScanReport) -> str:
    findings = "\n".join(
        f"""
        <article class="finding">
          <div class="finding-head">
            <strong>{html.escape(item.rule_id)} · {html.escape(item.title)}</strong>
            {_badge(item.severity)} {_badge(item.classification)}
          </div>
          <p>{html.escape(item.message)}</p>
          <dl>
            <dt>File</dt><dd>{_finding_location(item.path, item.line)}</dd>
            <dt>Recommendation</dt><dd>{html.escape(item.recommended or "")}</dd>
            <dt>Source</dt><dd>{_source_link(item.source_url, item.source_label)}</dd>
          </dl>
        </article>
        """
        for item in report.findings
    )
    if not findings:
        findings = (
            "<p>No supported findings detected. This is not exhausti"
            "ve compatibility or safety verification.</p>"
        )

    patches = "\n".join(
        f"""
        <article class="patch">
          <h3>{html.escape(item.path)} · {html.escape(item.rule_id)}</h3>
          <p>{html.escape(item.description)}</p>
          <pre>{html.escape(item.diff)}</pre>
        </article>
        """
        for item in report.patches
    )
    if not patches:
        patches = "<p>No deterministic patches generated.</p>"

    workflows = "\n".join(
        f"""
        <tr>
          <td>{html.escape(item.path)}</td>
          <td>{item.jobs}</td>
          <td>{item.steps}</td>
          <td>{item.actions}</td>
          <td>{item.local_actions}</td>
        </tr>
        """
        for item in report.workflow_summaries
    )
    if not workflows:
        workflows = '<tr><td colspan="5">No workflow files found.</td></tr>'

    notes = "".join(f"<li>{html.escape(note)}</li>" for note in report.notes)
    metric_scanned = _metric("Scanned files", len(report.scanned_files))
    metric_findings = _metric("Findings", len(report.findings))
    metric_blocking = _metric("Blocking", len(report.blocking_findings))
    metric_patches = _metric("Patches", len(report.patches))
    generated_line = (
        f"Generated {html.escape(report.created_at)} with rule pack "
        f"{html.escape(report.rule_pack_version)}"
    )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Actions Upgrade Guard Report</title>
    <style>
      body {{
        color: #152238;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.55;
        margin: 0;
        background: #f5f7fb;
      }}
      main {{
        margin: 0 auto;
        max-width: 1080px;
        padding: 32px 20px 56px;
      }}
      header, section, article {{
        background: #fff;
        border: 1px solid #d9e1ef;
        border-radius: 8px;
        margin-bottom: 18px;
        padding: 20px;
      }}
      h1, h2, h3 {{ line-height: 1.2; margin: 0 0 12px; }}
      .summary {{
        display: grid;
        gap: 12px;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      }}
      .metric {{
        background: #eef4ff;
        border-radius: 6px;
        padding: 12px;
      }}
      .metric strong {{ display: block; font-size: 1.4rem; }}
      .badge {{
        border-radius: 999px;
        display: inline-block;
        font-size: 0.78rem;
        margin-left: 6px;
        padding: 2px 8px;
        text-transform: uppercase;
      }}
      .badge-critical, .badge-high, .badge-manual_review, .badge-blocked {{
        background: #ffe8e6;
        color: #8b1d14;
      }}
      .badge-medium, .badge-autofix {{ background: #fff1c7; color: #6d4a00; }}
      .badge-info, .badge-informational {{ background: #e8f4ff; color: #16456b; }}
      table {{ border-collapse: collapse; width: 100%; }}
      th, td {{ border-bottom: 1px solid #d9e1ef; padding: 10px; text-align: left; }}
      pre {{
        background: #0f172a;
        border-radius: 6px;
        color: #e5eefb;
        overflow-x: auto;
        padding: 14px;
      }}
      dl {{
        display: grid;
        gap: 8px 14px;
        grid-template-columns: max-content 1fr;
      }}
      dt {{ color: #52627a; font-weight: 700; }}
      dd {{ margin: 0; }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <p>{generated_line}</p>
        <h1>Actions Upgrade Guard Report</h1>
        <p>Status: <strong>{html.escape(report.status)}</strong></p>
        <div class="summary">
          {metric_scanned}
          {metric_findings}
          {metric_blocking}
          {metric_patches}
        </div>
      </header>
      <section>
        <h2>Workflow Inventory</h2>
        <table>
          <thead>
            <tr>
              <th>Path</th><th>Jobs</th><th>Steps</th>
              <th>Actions</th><th>Local actions</th>
            </tr>
          </thead>
          <tbody>{workflows}</tbody>
        </table>
      </section>
      <section>
        <h2>Findings</h2>
        {findings}
      </section>
      <section>
        <h2>Patch Preview</h2>
        {patches}
      </section>
      <section>
        <h2>Notes</h2>
        <ul>{notes}</ul>
      </section>
    </main>
  </body>
</html>
"""


def _finding_location(path: str, line: int | None) -> str:
    suffix = f":{line}" if line else ""
    return html.escape(f"{path}{suffix}")


def _source_link(url: str, label: str) -> str:
    if not url:
        return html.escape(label or "not available")
    return f'<a href="{html.escape(url)}">{html.escape(label)}</a>'


def _metric(label: str, value: int) -> str:
    return (
        '<div class="metric">'
        f"<span>{html.escape(label)}</span><strong>{value}</strong>"
        "</div>"
    )
