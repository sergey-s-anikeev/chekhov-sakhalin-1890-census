# MySQL Import Guide — Sakhalin 1890 English Dataset

## Requirements

- MySQL 8.0 or later;
- a database created by the user;
- `local_infile=ON` on the server;
- the MySQL client started with `--local-infile=1`;
- UTF-8 (`utf8mb4`) throughout.

The candidate CSV is `data/analytical/sakhalin_1890_en_v1.csv`. Its approved
SHA-256 is
`1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508`.

## Import sequence

1. Select the target database.
2. Run `sql/01_create_english_dataset.sql`.
3. If the repository is not at the documented Windows path, edit only the CSV
   path in `sql/02_load_english_dataset.sql`.
4. Start the MySQL client with local loading enabled and run
   `sql/02_load_english_dataset.sql`.
5. Review `SHOW WARNINGS`; a clean import should not produce conversion or
   truncation warnings.
6. Run `sql/03_validate_english_dataset.sql`. Every row in the first result set
   must be `PASS`, and the duplicate-sequence and Cyrillic queries must return
   zero rows.
7. Use `sql/04_analysis_queries.sql` for initial analysis and Tableau
   reconciliation.

Example client invocation:

```powershell
mysql --local-infile=1 -u YOUR_USER -p YOUR_DATABASE
```

Then, from the MySQL prompt:

```sql
SOURCE C:/Users/User/Documents/Work/sakhalin_1890/sql/01_create_english_dataset.sql;
SOURCE C:/Users/User/Documents/Work/sakhalin_1890/sql/02_load_english_dataset.sql;
SOURCE C:/Users/User/Documents/Work/sakhalin_1890/sql/03_validate_english_dataset.sql;
```

## NULL and Boolean handling

Empty nullable CSV fields are converted to SQL `NULL` during loading. Recorded
numeric zeroes remain zero. `allowance_status` is loaded as nullable Boolean:
CSV `TRUE` becomes `1`, CSV `FALSE` becomes `0`, and blank becomes SQL `NULL`.

## Safe reruns

The load script does not truncate or delete data. Run it against a newly created
or empty table. A second load into the populated table fails on primary-key
duplicates, preventing silent duplication. If replacement is intended, back up
the table and explicitly clear or replace it under normal database-change
controls.

## MySQL Workbench procedure

The local `MySQL80` service is installed and running. In MySQL Workbench:

1. Open your local MySQL connection.
2. Create a schema named `sakhalin_1890`, or select another empty target schema.
3. Double-click the schema so its name appears bold as the default schema.
4. Run `SHOW GLOBAL VARIABLES LIKE 'local_infile';`.
5. If the value is `OFF` and your account has administrative permission, run
   `SET GLOBAL local_infile = ON;`, then reconnect.
6. If Workbench reports that local data loading is disabled on the client, edit
   the connection, open **Advanced**, add `OPT_LOCAL_INFILE=1` under **Others**,
   save, and reconnect.
7. Open and execute the numbered SQL scripts in order. Use the lightning-bolt
   button to execute the complete script.
8. In the validation script, every summary row must report `PASS`; the duplicate
   sequence and Cyrillic queries must return zero rows.

`LOAD DATA LOCAL` must be permitted by both the server and client. Restrict it
to this controlled import workflow and disable it again afterward if required
by your security policy.

## Current testing status

The SQL package was checked against the approved schema, actual maximum field
lengths, expected category totals, and MySQL 8 syntax conventions. The user's
Workbench connection successfully loaded 7,446 rows into `sakhalin_1890_en`
with zero skipped records and zero warnings. The validation result set matched
the expected CSV QA totals and all displayed controls returned `PASS`.
