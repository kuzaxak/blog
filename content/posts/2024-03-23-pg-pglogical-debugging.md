---
title: "Debugging PgLogical Replication"
description: "Learn how to debug PgLogical replication issues in PostgreSQL, covering both provider and receiver sides."
tags: ["postgres", "pglogical", "wal"]
date: 2024-03-23
slug: "pg-pglogical-debugging"
tldr: |
  Check replication delay and WAL file on the provider side using pg_replication_slots and pg_stat_replication.
  Investigate replication status on the receiver side using pglogical.show_subscription_status() and pglogical.local_sync_status.
  Restart the subscription by recreating it with the same parameters, optionally turning off init sync for large databases.
  Request a full resync per table using pglogical.alter_subscription_resynchronize_table() if needed.
---

PgLogical is a powerful logical replication system for PostgreSQL that allows you to replicate data between databases. However, like any complex system, it can sometimes encounter issues. In this article, we'll explore how to debug PgLogical replication problems on both the provider and receiver sides.

## Provider Side Debugging

On the provider side, you can check the delay in data and the current linked WAL file by running the following query:

```sql
SELECT slot_name, database,
       lpad((pg_control_checkpoint()).timeline_id::text, 8, '0') ||
       lpad(split_part(restart_lsn::text, '/', 1), 8, '0') ||
       lpad(substr(split_part(restart_lsn::text, '/', 2), 1, 2), 8, '0') AS wal_file,
	   pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS replication_delay
FROM pg_replication_slots WHERE plugin like '%pglogical%';
```

In my case, I had a delay of 170GB for one particular database where I had PgLogical enabled. To clarify the status of the replication slot, you can run:

```sql
select   pid, client_addr, application_name, state, sync_state,
         pg_wal_lsn_diff(pg_current_wal_lsn(),sent_lsn) AS sent_lag,
         pg_wal_lsn_diff(sent_lsn,flush_lsn) AS receiving_lag,
         pg_wal_lsn_diff(flush_lsn,replay_lsn) AS replay_lag,
         pg_wal_lsn_diff(pg_current_wal_lsn(),replay_lsn) AS total_lag,
         now()-reply_time AS reply_delay
from pg_stat_replication;
```
Pay attention to the `reply_delay` column, which indicates the time when the provider last received an update from the subscriber database.

If you see `catchup` in some slots, it means that your receiver is lagging behind, and you need to switch to it to investigate the reason.

## Receiver Side Debugging

On the receiver side, you can start the investigation from the replication status. Repeat the following query for each logical database that you have configured with PgLogical:

```sql
SELECT subscription_name, status FROM pglogical.show_subscription_status();
```

If you see `down` status, you can check logs and grep for `pglogical apply` and then `ERROR`. You may have some conflicts in schema.

Log messages may look like:

```
[2641263]: [5-1] 65705192.284d6f 1848030187 databse_name [unknown] pglogical apply 16794:4247138421 ERROR: null value in column "ccy" of relation "report" violates not-null constraint
```

If the replication status is `replicating`, you can investigate further by running the following query to get data per table for the synced database:

```sql
SELECT 
	CASE sync_kind
		WHEN 'i' THEN 'Init'
		WHEN 'f' THEN 'Full'
		WHEN 's' THEN 'Structure'
		WHEN 'd' THEN 'Data'
		ELSE 'Unknown kind'
    END AS sync_kind,
	sync_subid,
	sync_nspname || '.' || sync_relname as relation,
    CASE sync_status
        WHEN '\0' THEN 'No sync'
        WHEN 'i' THEN 'Ask for sync'
        WHEN 's' THEN 'Sync structure'
        WHEN 'd' THEN 'Data sync'
        WHEN 'c' THEN 'Constraint sync (post-data structure)'
        WHEN 'w' THEN 'Table sync is waiting to get OK from main thread'
        WHEN 'u' THEN 'Catching up'
        WHEN 'y' THEN 'Synchronization finished (at lsn)'
        WHEN 'r' THEN 'Done'
        ELSE 'Unknown status'
    END AS sync_status,
	sync_statuslsn
FROM 
    pglogical.local_sync_status;
```

If you see `Done` or `Synchronization finished` for some tables but the data is missing, you may need to re-sync tables or restart the replication, you may read more in the [issue][1]. Before doing so, save the results from the `local_sync_status` table, as they will be lost after restarting the replication.

You can attempt to resync specific tables before recreating the entire replication:

```sql
SELECT pglogical.alter_subscription_resynchronize_table(
  subscription_name := 'subscription_name',
  relation := 'public.table_name'
);
```

**NB!:** Remember it will truncate table first. Do it outside of normal operations hours!

If nothing helps, you can restart the replication using the following helper query to build a command with the same parameters as before. If your database is big enough (>100GB), you can turn off init sync for the data.

```sql
SELECT 'SELECT pglogical.drop_subscription(''' || sub_name || ''');' 
	   || 'SELECT pglogical.create_subscription('
       || 'subscription_name := ''' || sub_name || ''', '
       || 'provider_dsn := ''' || provider_dsn || ''', '
	   || 'replication_sets := ''{' || array_to_string(replication_sets, ',') || '}'', '
       || 'synchronize_data := false);' AS create_subscription_cmd
FROM (
  SELECT subscription_name as sub_name,
         provider_dsn,
		 replication_sets
  FROM pglogical.show_subscription_status()
) t;
```

This query will template a query to restart the subscription in a database by recreating it. It will reduce the lag but will repoint the slot to the latest state, so the data lag won't be synced.

After restarting the subscription, the records from `local_sync_status` will be lost. To overcome this, you can request a full resync (truncate, copy, sync) per table using the data from the `local_sync_status` table:

```sql
SELECT pglogical.alter_subscription_resynchronize_table(
  subscription_name := 'subscription_name',
  relation := 'public.table_name'
);
```

**NB!:** Remember it will truncate table first. Do it outside of normal operations hours!

After triggering resync you will see that table got added to the `local_sync_status` with a status `Data sync` or `Ask for sync`.

[1]: https://github.com/2ndQuadrant/pglogical/issues/204