#! /usr/bin/env python3
import datetime
import os
import tempfile
from pathlib import Path
from typing import Optional

import typer

import boto3
import simplejson as json


def backup_table(
    table_name: str = typer.Argument(..., help="The name of the table to back up"),
    output_dir: Path = typer.Argument(
        ..., help="Directory to save the backup json file."
    ),
    base_file_name: Optional[str] = typer.Option(
        None, help="Filename other than the table name"
    ),
    timestamp: bool = typer.Option(True, help="include a timestamp in the file name"),
    endpoint_url: Optional[str] = typer.Option(
        None, help="Use an endpoint other than default dynamodb"
    ),
    aws_access_key_id: Optional[str] = typer.Option(
        None, help="AWS Access Key ID", envvar="ACCESS_KEY"
    ),
    aws_secret_access_key: Optional[str] = typer.Option(
        None, help="AWS Secret Access Key", envvar="SECRET_KEY"
    ),
    region_name: Optional[str] = typer.Option(
        "us-east-1", help="AWS Region", envvar="REGION"
    ),
    generate_report: Optional[str] = typer.Option(
        None, help="Generate report as 'json' or 'pdf"
    ),
    info_file: Optional[Path] = typer.Option(
        None,
        help="Python file containing OrderedDict of attributes and display names"
        "and title for the pdf version of the report if applicable",
    ),
):
    """Backup a dynamodb table to a local file"""
    db = boto3.resource(
        "dynamodb",
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )
    table = db.Table(table_name)
    res = table.scan()
    last_evaluated_key = res.get("LastEvaluatedKey")
    items = res["Items"]
    while last_evaluated_key:
        res = table.scan(ExclusiveStartKey=last_evaluated_key)
        items.extend(res["Items"])
        last_evaluated_key = res.get("LastEvaluatedKey")

    base_file_name = base_file_name or table_name
    if timestamp:
        output_name = (
            f"{base_file_name}_{datetime.datetime.utcnow().strftime('%Y-%m-%d_%H%M')}"
        )
    else:
        output_name = base_file_name
    output_file_path = Path(output_dir) / f"{output_name}.json"

    if generate_report:
        report_dir = Path(output_dir) / "reports"
        os.makedirs(report_dir, exist_ok=True)
        report_file_name = (
            f"changes_{base_file_name}_"
            f"{datetime.datetime.utcnow().strftime('%Y-%m-%d_%H%M')}"
        )
        rep_data = generate_differences(items, base_file_name, output_dir)
        rep_data = sorted(rep_data, key=lambda item: item.get("new").get("number"))
        if "json" in generate_report and rep_data:
            with (report_dir / f"{report_file_name}.json").open("w") as report_f:
                json.dump(rep_data, report_f)
        if "pdf" in generate_report and rep_data:
            import render_report

            tmp_path = Path(tempfile.mkdtemp())
            html_path = tmp_path / f"{report_file_name}.html"
            pdf_path = report_dir / f"{report_file_name}.pdf"
            render_report.render_html(
                str(Path(info_file).absolute()), rep_data, html_path
            )
            render_report.to_pdf(html_path, pdf_path)

    with output_file_path.open("w") as backupjson:
        json.dump(items, backupjson)


def generate_differences(new_data: list, base_file_name: str, output_dir):
    updated_items = []
    # Look pretty code
    backup_files = sorted(
        [item for item in os.listdir(output_dir) if base_file_name in item]
    )
    # Lists the output directory, filters on backups with the same base file name,
    # sorts it,
    if not backup_files:
        return []

    last_backup_file = backup_files[-1]

    with (Path(output_dir) / last_backup_file).open("r") as last_backup_data:
        old_data = json.load(last_backup_data)

    old_data_indexed = {item["id"]: item for item in old_data}

    for new_item in new_data:
        if (old_item := old_data_indexed.get(new_item["id"])) is not None:
            for k, v in new_item.items():
                if old_item.get(k) != v:
                    updated_items.append({"old": old_item, "new": new_item})
                    break
        else:
            updated_items.append({"new": new_item})

    return updated_items


if __name__ == "__main__":
    typer.run(backup_table)
