"""Text, JSON and HTML reports for a batch analysis."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, select_autoescape

from .models import BatchMetrics

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>HLA imputation analysis: {{ metrics.batch_id }}</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto;
       padding: 0 1rem; line-height: 1.5; color: #222; }
.status { padding: 2px 8px; border-radius: 4px; font-weight: bold; }
.SUCCESS { background: #d4edda; } .WARNING { background: #fff3cd; }
.FAILURE { background: #f8d7da; } .UNKNOWN { background: #eee; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: 6px; border-bottom: 1px solid #ddd; }
pre { background: #f4f4f4; padding: 8px; overflow-x: auto; }
</style>
</head>
<body>
<h1>HLA imputation analysis</h1>
<p><strong>Batch:</strong> {{ metrics.batch_id }}<br>
<strong>Analysed:</strong> {{ metrics.timestamp }}<br>
<strong>Status:</strong>
<span class="status {{ metrics.status.value }}">{{ metrics.status.value }}</span></p>
{% if metrics.errors %}<h2>Errors</h2><ul>
{% for e in metrics.errors %}<li>{{ e }}</li>{% endfor %}</ul>{% endif %}
{% if metrics.warnings %}<h2>Warnings</h2><ul>
{% for w in metrics.warnings %}<li>{{ w }}</li>{% endfor %}</ul>{% endif %}
{% if metrics.command %}<h2>Beagle command found in log</h2>
<pre>{{ metrics.command.raw_command }}</pre>{% endif %}
<h2>Files</h2>
<table><thead><tr><th>File</th><th>Type</th><th>Bytes</th><th>Modified</th></tr></thead>
<tbody>
{% for f in metrics.input_files + metrics.output_files + metrics.logs %}
<tr><td>{{ f.path.name }}</td><td>{{ f.file_type.value }}</td>
<td>{{ f.size_bytes }}</td><td>{{ f.last_modified }}</td></tr>
{% endfor %}
</tbody></table>
</body>
</html>
"""


class ReportGenerator:
    """Write analysis results in text, JSON or HTML."""

    @staticmethod
    def render_text(metrics: BatchMetrics) -> str:
        lines = [
            f"Batch: {metrics.batch_id}",
            f"Status: {metrics.status.value}",
            f"Outputs found: {len(metrics.output_files)}; "
            f"missing: {', '.join(metrics.missing_artifacts) or 'none'}",
        ]
        lines += [f"ERROR {e}" for e in metrics.errors]
        lines += [f"WARNING {w}" for w in metrics.warnings]
        if metrics.command:
            lines.append(f"Beagle command: {metrics.command.raw_command}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def generate_text(metrics: BatchMetrics, output_path: Path) -> None:
        Path(output_path).write_text(ReportGenerator.render_text(metrics))

    @staticmethod
    def generate_json(metrics: BatchMetrics, output_path: Path) -> None:
        Path(output_path).write_text(metrics.model_dump_json(indent=2))

    @staticmethod
    def generate_html(metrics: BatchMetrics, output_path: Path) -> None:
        # Autoescape: log lines are copied into the page and may contain '<'.
        env = Environment(autoescape=select_autoescape(default=True))
        html = env.from_string(HTML_TEMPLATE).render(metrics=metrics)
        Path(output_path).write_text(html)
