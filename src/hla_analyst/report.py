import json
from pathlib import Path
from typing import List
from datetime import datetime
from jinja2 import Template

from .models import BatchMetrics

class ReportGenerator:
    """Generates reports in various formats."""

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HLA Imputation Analysis Report</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { border-bottom: 2px solid #eaeaea; padding-bottom: 10px; }
            .status { padding: 5px 10px; border-radius: 4px; font-weight: bold; display: inline-block; }
            .status-SUCCESS { background-color: #d4edda; color: #155724; }
            .status-FAILURE { background-color: #f8d7da; color: #721c24; }
            .status-WARNING { background-color: #fff3cd; color: #856404; }
            .section { margin-top: 30px; background: #f9f9f9; padding: 20px; border-radius: 8px; }
            code { background: #eee; padding: 2px 5px; border-radius: 3px; }
            pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>HLA Imputation Analysis Report</h1>
        
        <div class="section">
            <h2>Batch Summary</h2>
            <p><strong>Batch ID:</strong> {{ metrics.batch_id }}</p>
            <p><strong>Date:</strong> {{ metrics.timestamp }}</p>
            <p><strong>Status:</strong> <span class="status status-{{ metrics.status }}">{{ metrics.status }}</span></p>
        </div>

        {% if metrics.errors %}
        <div class="section" style="border-left: 5px solid #dc3545;">
            <h2 style="color: #dc3545;">Errors Detected</h2>
            <ul>
            {% for error in metrics.errors %}
                <li>{{ error }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if metrics.command %}
        <div class="section">
            <h2>Execution Command</h2>
            <p><strong>JAR:</strong> {{ metrics.command.jar_path }}</p>
            <p><strong>Memory:</strong> {{ metrics.command.memory_setting }}</p>
            <pre>{{ metrics.command.raw_command }}</pre>
        </div>
        {% endif %}

        <div class="section">
            <h2>File Artifacts</h2>
            <table>
                <thead>
                    <tr>
                        <th>File Name</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Last Modified</th>
                    </tr>
                </thead>
                <tbody>
                {% for file in metrics.input_files + metrics.output_files + metrics.logs %}
                    <tr>
                        <td>{{ file.path.name }}</td>
                        <td>{{ file.file_type }}</td>
                        <td>{{ file.size_bytes }} bytes</td>
                        <td>{{ file.last_modified }}</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    @staticmethod
    def generate_json(metrics: BatchMetrics, output_path: Path):
        """Generates a JSON report."""
        with open(output_path, 'w') as f:
            f.write(metrics.model_dump_json(indent=2))

    @staticmethod
    def generate_html(metrics: BatchMetrics, output_path: Path):
        """Generates an HTML report."""
        template = Template(ReportGenerator.HTML_TEMPLATE)
        html_content = template.render(metrics=metrics)
        with open(output_path, 'w') as f:
            f.write(html_content)
