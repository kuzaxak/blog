---
title: "Rapid WAL Growth in Postgres PG15 on Kubernetes"
description: |
    Dive into a deep tech exploration of dealing with rapidly growing Write-Ahead Logging (WAL) in 
    PostgreSQL PG15 within a Kubernetes environment. Learn about the challenges, mistakes made, and 
    the recovery process, complete with practical SQL queries and commands. 
    Essential reading for database administrators and engineers.
tags: ["postgres", "pglogical", "wal", "patroni"]
date: 2023-08-17
slug: "pg-wal-pilling-up"
tldr: |
   After upgrading to PostgreSQL PG15 in a Kubernetes cluster, we encountered rapid WAL growth. 
   A series of missteps led to replication issues. This article details the investigation process, 
   errors made, and how we successfully recovered the database. Key takeaways emphasize the importance 
   of understanding the root cause and ensuring backups before making significant changes.
--- 

## Intro

Our setup consists of two clusters, each with two nodes interconnected through logical replication managed by the [Patroni PostgreSQL operator][3].

```
 Prod                   
+---------+    logical replication     +----------+
| Primary | <---------------------->   | Replica  |
+---------+   (managed by patroni)     +----------+
    | |
    | | logical replication (pglogical)
    | |
    v v
+---------+    logical replication     +----------+
| Primary | <---------------------->   | Replica  |
+---------+   (managed by patroni)     +----------+
 SIT (Beta)
```

After upgrading to PostgreSQL 15, we received an alert about rapidly growing WAL files. The root cause was not immediately apparent, prompting an investigation.
What follows is an account of our endeavors to mitigate this issue and the pivotal 
lessons we learned along the way.

## Investigation and Missteps

In an attempt to resolve the issue, we came across a [recommendation][1] to inspect the latest checkpoint file using the pg_controldata command.

```
root@main-db-1:/home/postgres# pg_controldata -D /home/postgres/pgdata/pgroot/data
...
Latest checkpoint's REDO WAL file: 00000001000012A5000000E2
...
```

Noticing that files in `data/pg_wal/archive_status/` had been renamed with `.done` extensions, we proceeded to manually remove them using the `pg_archivecleanup` command to reclaim space.

```
pg_archivecleanup -d /home/postgres/pgdata/pgroot/data/pg_wal 00000001000012A5000000E0
pg_archivecleanup: keeping WAL file "/home/postgres/pgdata/pgroot/data/pg_wal/00000001000012A5000000E0" and later
pg_archivecleanup: removing file "/home/postgres/pgdata/pgroot/data/pg_wal/00000001000012A4000000FE"
pg_archivecleanup: removing file "/home/postgres/pgdata/pgroot/data/pg_wal/00000001000012A20000007D"
...
```

However, this action inadvertently disrupted the replication on the secondary node. To verify the replication status, we ran the following query on the receiver side (beta):

```sql
\c database_name
select subscription_name, status FROM pglogical.show_subscription_status();
```

The output confirmed that the replication was down:

```
    subscription_name    | status
-------------------------+--------
 sit_main_db             | down
(1 row)
```

To gain further insights, we used another [query][2] to check the replication slots and their associated WAL files on the sender side (prod):

```sql
SELECT slot_name,
       lpad((pg_control_checkpoint()).timeline_id::text, 8, '0') ||
       lpad(split_part(restart_lsn::text, '/', 1), 8, '0') ||
       lpad(substr(split_part(restart_lsn::text, '/', 2), 1, 2), 8, '0')
       AS wal_file
FROM pg_replication_slots;
```

The results highlighted the WAL files that were inadvertently deleted:

```
 main_db_0                               | 00000001000012A5000000E5
 pgl_bonds_prod_a869e54_sit_mfd26307     | 00000001000012A10000007C
 pgl_import_prod_f3ab9f4_sit_mc9d8484    | 00000001000012A10000007C
 pgl_prod_828fc61_sit_meced8c6           | 00000001000012A10000007C
 pgl_data_prod_0c0d721_sit_m6d604ee      | 00000001000012A10000007C
 pgl_sentiment_prod_3b3f93a_sit_m5397d6e | 00000001000012A10000007C
```

## Recovery Process

Fortunately, we had WAL files stored in S3 using wal-g for point-in-time recovery. Instead of manually restoring with wal-g, we decided to initialize a fresh instance in the Patroni cluster:

```shell
patronictl reinit main-db main-db-0
...
```

After restoring the WAL to its original state, we initiated a failover:

```shell
patronictl failover
...
```

We then restarted the replication and used the following query on the source database to monitor the replication lag for our most data-intensive database:

```sql
select   pid, client_addr, application_name, state, sync_state,
         pg_wal_lsn_diff(pg_current_wal_lsn(),sent_lsn) AS sent_lag,
         pg_wal_lsn_diff(sent_lsn,flush_lsn) AS receiving_lag,
         pg_wal_lsn_diff(flush_lsn,replay_lsn) AS replay_lag,
         pg_wal_lsn_diff(pg_current_wal_lsn(),replay_lsn) AS total_lag,
         now()-reply_time AS reply_delay
from pg_stat_replication;
```

The output showed the replication lag for each subscriber:

```
  pid  | client_addr |        application_name         |   state   | sync_state |  write_lag  |  flush_lag  | replay_lag
-------+-------------+---------------------------------+-----------+------------+-------------+-------------+-------------
 75525 | 10.23.8.19  | sit_main_db                     | catchup   | async      | -9811896992 | -9811896992 | -9811896992
 65825 | 10.23.8.24  | sit_main_db_import              | streaming | async      |           0 |           0 |           0
 65827 | 10.23.8.57  | sit_main_db_market_sentiment    | streaming | async      |           0 |           0 |           0
 65828 | 10.23.8.40  | sit_main_db_market_data         | streaming | async      |           0 |           0 |           0
 65826 | 10.23.8.57  | sit_main_db_bonds               | streaming | async      |           0 |           0 |           0
 79684 | 10.24.134.7 | main-db-1                       | streaming | async      |           0 |           0 |           0
```

Eventually, the replication caught up, and WAL files were properly managed and removed from the disk.

```
postgres=# SELECT slot_name,
       lpad((pg_control_checkpoint()).timeline_id::text, 8, '0') ||
       lpad(split_part(restart_lsn::text, '/', 1), 8, '0') ||
       lpad(substr(split_part(restart_lsn::text, '/', 2), 1, 2), 8, '0')
       AS wal_file
FROM pg_replication_slots;
                      slot_name                |         wal_file
-----------------------------------------------+-------------------------
 main_db_1                                     | 00000002000012A6000000BE
 pgl_bonds_prod_a869e54_sit_mfd26307           | 00000002000012A6000000BE
 pgl_import_prod_f3ab9f4_sit_mc9d8484          | 00000002000012A6000000BE
 pgl_prod_828fc61_sit_meced8c6                 | 00000002000012A6000000BE
 pgl_data_prod_0c0d721_sit_m6d604ee            | 00000002000012A6000000BE
 pgl_sentiment_prod_3b3f93a_sit_m5397d6e       | 00000002000012A6000000BE
```

## Additional Tips for Debugging pglogical Replication

1. Monitor the replication delay on the provider side:

```sql
SELECT slot_name,
       lpad((pg_control_checkpoint()).timeline_id::text, 8, '0') ||
       lpad(split_part(restart_lsn::text, '/', 1), 8, '0') ||
       lpad(substr(split_part(restart_lsn::text, '/', 2), 1, 2), 8, '0')
       AS wal_file,
	   pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS replication_delay
FROM pg_replication_slots;
```

2. Check per table status on receiver side:

```sql
SELECT * FROM pglogical.local_sync_status;
```

## Takeaways

- **Root Cause Analysis**: Before making any amendments, always attempt to identify the root cause of the problem.
- **Preemptive Backups**: Prior to deleting any files, especially critical ones, ensure you have a backup in place.
- **Educate Yourself**: Dive deeper into how systems like WAL function. One article is seldom enough; broadening your knowledge base can help in averting potential crises.


[1]: https://www.postgresql.fastware.com/blog/how-to-solve-the-problem-if-pg-wal-is-full
[2]: https://stackoverflow.com/questions/49539938/postgres-wal-file-not-getting-deleted
[3]: https://github.com/zalando/postgres-operator
