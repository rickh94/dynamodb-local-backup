# dynamodb-local-backup
Docker container to make a local json backup of a dynamodb table. Also has a restore script

## Backup

In the container:
 
bash`python3 backup.py TABLE_NAME OUTPUT_DIR`

Backs up TABLE_NAME to a json file in OUTPUT_DIR

You can get the file out of the container in the usual ways (probably a volume)


## Restore

In the container:

bash`python3 restore.py TABLE_NAME BACKUP_FILE`

Restores TABLE_NAME (should probably be a new empty table) from BACKUP_FILE.


## Typer

This was built with [Typer](https://typer.tiangolo.com/), and has all the help and functionality you'd expect. 
