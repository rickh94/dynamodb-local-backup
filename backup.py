#! /usr/bin/env python3
import datetime
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
        base_file_name = (
            f"{base_file_name}_{datetime.datetime.utcnow().strftime('%Y-%m-%d_%H%M')}"
        )
    output_file_path = Path(output_dir) / f"{base_file_name}.json"
    with output_file_path.open("w") as backupjson:
        json.dump(items, backupjson)


if __name__ == "__main__":
    typer.run(backup_table)
