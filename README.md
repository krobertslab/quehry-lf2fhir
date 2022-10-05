# quehry-lf2fhir

Python code that is part of the QUEHRY project. Responsible for converting the logical form representation to FHIR queries.

## Dependencies

### Libraries

Tested with Python 3.8.12.

All the required libraries present in [`requirements.txt`](requirements.txt).

### FHIR server from MITRE

Follow the instructions provided at the repository below to build and run a FHIR server locally.

* https://github.com/mitre/fhir-server

Use the mongo data backup ([`data/mongo_fhir_dump.tar.gz`](data/mongo_fhir_dump.tar.gz)) to populate your FHIR server. Refer to the [mongodb documentation](https://www.mongodb.com/docs/manual/tutorial/backup-and-restore-tools/) for how to restore a backup.

## Run

Called directly from the [`olympia-quehry`](https://github.com/krobertslab/olympia-quehry) repository.

Can also be called using the [`fhir_driver.py`](src/data/fhir_driver.py) script.
