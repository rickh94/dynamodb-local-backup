#! /usr/bin/env python3
from pathlib import Path
from typing import Optional

import boto3
import simplejson as json
import typer


def restore_table(
    table_name: str = typer.Argument(
        ..., help="The name of the table to restore to. This table must already exist"
    ),
    backup_file: Path = typer.Argument(
        ..., help="The file to read the backup data from"
    ),
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
    """Restore a dynamodb table from a backup file"""
    db = boto3.resource(
        "dynamodb",
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )
    table = db.Table(table_name)
    backup_file = Path(backup_file)
    with backup_file.open("r") as backupjson:
        items = json.load(backupjson)
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


if __name__ == "__main__":
    typer.run(restore_table)
