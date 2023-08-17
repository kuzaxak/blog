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

We manage two clusters, each comprising of two nodes interconnected through logical replication. 
Our chosen tool to manage databases within Kubernetes is the patroni [postgres operator][3].

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

After the PG15 upgrade, we received an alert notifying us of a rapidly growing WAL,
at this point is wasn't clear what is a root cause for such behaviour. 
What follows is an account of our endeavors to mitigate this issue and the pivotal 
lessons we learned along the way.

## Research and Breaking Things

Mistakes were made. While scouring the internet for solutions, 
we stumbled upon a [recommendation][1] which prompted us to inspect the latest checkout file.

```
root@main-db-1:/home/postgres# pg_controldata -D /home/postgres/pgdata/pgroot/data
...
Latest checkpoint's REDO WAL file: 00000001000012A5000000E2
...
```

After observing the `REDO WAL file: 00000001000012A5000000E2`, and noting that files
had been renamed in `data/pg_wal/archive_status/` to `.done` extensions, 
I initiated manual removal to reclaim space using the `pg_archivecleanup` command.

```
pg_archivecleanup -d /home/postgres/pgdata/pgroot/data/pg_wal 00000001000012A5000000E0
pg_archivecleanup: keeping WAL file "/home/postgres/pgdata/pgroot/data/pg_wal/00000001000012A5000000E0" and later
pg_archivecleanup: removing file "/home/postgres/pgdata/pgroot/data/pg_wal/00000001000012A4000000FE"
pg_archivecleanup: removing file "/home/postgres/pgdata/pgroot/data/pg_wal/00000001000012A20000007D"
...
```

Job completed, only to realize replication on the secondary had halted. 
The replication wasn't just paused; it was thoroughly disrupted.

```sql
select subscription_name, status FROM pglogical.show_subscription_status();
    subscription_name    | status
-------------------------+--------
 sit_main_db             | down
(1 row)
```

A [query][2] provided further insights:

```sql
SELECT slot_name,
       lpad((pg_control_checkpoint()).timeline_id::text, 8, '0') ||
       lpad(split_part(restart_lsn::text, '/', 1), 8, '0') ||
       lpad(substr(split_part(restart_lsn::text, '/', 2), 1, 2), 8, '0')
       AS wal_file
FROM pg_replication_slots;
```

The results highlighted the files I'd inadvertently deleted. 

```
 main_db_0                               | 00000001000012A5000000E5
 pgl_bonds_prod_a869e54_sit_mfd26307     | 00000001000012A10000007C
 pgl_import_prod_f3ab9f4_sit_mc9d8484    | 00000001000012A10000007C
 pgl_prod_828fc61_sit_meced8c6           | 00000001000012A10000007C
 pgl_data_prod_0c0d721_sit_m6d604ee      | 00000001000012A10000007C
 pgl_sentiment_prod_3b3f93a_sit_m5397d6e | 00000001000012A10000007C
```

Thankfully, we utilized wal-g for WAL storage in our S3 for point-in-time recovery.

## Recovery

While a manual `wal-g` restoration was on the cards, the complexity urged me to freshly 
initialize another instance in the `patroni` cluster.

```shell
patronictl reinit main-db main-db-0
...
```

Having restored the WAL to its original state, I initiated a failover:

```shell
patronictl failover
...
```

I restarted the replication and discovered a query that showcased the replication lag for our most data-intensive database:

```sql
select   pid, client_addr, application_name, state, sync_state,
         pg_wal_lsn_diff(sent_lsn, write_lsn) as write_lag,
         pg_wal_lsn_diff(sent_lsn, flush_lsn) as flush_lag,
         pg_wal_lsn_diff(sent_lsn, replay_lsn) as replay_lag
from pg_stat_replication;
```

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

After a while, the replication caught up, and WAL files were appropriately managed and removed from the disk.

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

## Takeaways

- **Root Cause Analysis**: Before making any amendments, always attempt to identify the root cause of the problem.
- **Preemptive Backups**: Prior to deleting any files, especially critical ones, ensure you have a backup in place.
- **Educate Yourself**: Dive deeper into how systems like WAL function. One article is seldom enough; broadening your knowledge base can help in averting potential crises.


[1]: https://www.postgresql.fastware.com/blog/how-to-solve-the-problem-if-pg-wal-is-full
[2]: https://stackoverflow.com/questions/49539938/postgres-wal-file-not-getting-deleted
[3]: https://github.com/zalando/postgres-operator
