# Urban City 311 — Azure Data Engineering Project

## Project Overview

This project implements an Azure data engineering pipeline
for processing NYC 311 service-request data.

## Technologies Used

- Python
- Apache Airflow
- Terraform
- Azure Blob Storage
- Azure Data Factory
- Azure Database for PostgreSQL
- SQL
- Parquet

## Architecture

1. Python processes source data into Parquet format.
2. Azure Blob Storage stores the processed dataset in the Silver layer.
3. Azure Data Factory copies the Parquet data into PostgreSQL.
4. PostgreSQL stores the records for analytical queries.
5. A separate Data Factory pipeline performs data-quality checks.

## Verified Pipeline Results

- Source records read: 4,289,440
- Records copied: 4,289,440
- Destination PostgreSQL records: 4,289,440
- Copy activity status: Succeeded
- Data validation activity status: Succeeded

## Data Quality Results

| Check | Records | Percentage |
|---|---:|---:|
| Missing creation dates | 0 | 0.00% |
| Missing problem descriptions | 0 | 0.00% |
| Missing city values | 225,478 | 5.26% |
| Missing closure dates | 185,391 | 4.32% |
| Missing coordinates | 86,893 | 2.03% |
| Invalid coordinate ranges | 0 | 0.00% |

## Findings

All 4,289,440 source records were successfully copied
into the PostgreSQL destination.

Missing city values and coordinates should be considered
when performing location-based analysis.

Missing closure dates may represent requests that
remain open.

## Limitations

- Duplicate-record detection has not been completed.
- Data-quality categories may overlap.
- Incremental loading has not yet been implemented.
- Re-running the existing copy pipeline may create duplicates.

## Security

Azure Data Factory uses an approved managed private
endpoint to connect to PostgreSQL.

Passwords, credentials, Terraform state, and local
environment configuration must not be committed to GitHub.
