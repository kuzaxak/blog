---
title: "Upgrading PostgreSQL from 14 to 15 using Patroni in Kubernetes"
description: |
    This article provides a detailed guide on how to upgrade PostgreSQL from version 
    14 to 15 using Patroni in Kubernetes. It covers the necessary preparations, including 
    enabling in-place upgrades and failsafe mode, starting the upgrade, and fixing broken 
    pglogical replication. It also addresses a specific issue related to pglogical 
    replication and provides a solution for it.
tags: ["postgres", "pglogical", "wal", "patroni"]
date: 2023-08-28
slug: "pg-upgrade-15"
tldr: |
    To fix broken pglogical you need to recreate origin with the same name as replication slot.
    `SELECT * FROM pg_stat_replication_slots; SELECT pg_replication_origin_create('pgl_market_data_prod_0c0d721_sit_m6d604ee');`
thumbnail: ./art-cover.webp
resources:
- src: ./art-cover.webp
---

![image](./art-cover.webp)

We recently undertook the task of upgrading PostgreSQL (PG) from version 14 to 15. 
For this, we used Patroni to control the PG deployment in Kubernetes (k8s).

## Enabling In-Place Upgrade

Initially, to start a deployment, we needed to enable the in-place upgrade option in the 
PostgreSQL operator:

```yaml
configMajorVersionUpgrade:
  # operator will run the upgrade script after the manifest is updated and pods are rotated
  major_version_upgrade_mode: manual
```

## Enabling Failsafe Mode

Next, we decided to enable the [failsafe mode][2] to reduce the number of failovers in a cluster.

```yaml
configPatroni:
  # enable Patroni DCS failsafe_mode feature
  enable_patroni_failsafe_mode: true
```

We experienced quite a lot of failovers due to temporary k8s API unavailability.

## Starting the Upgrade

With all preparations done, we started the upgrade by updating the PostgresCluster manifests:

```yaml
apiVersion: acid.zalan.do/v1
kind: postgresql
spec:
  allowedSourceRanges: null
  postgresql:
    version: 14 -> 15
```

The upgrade itself went smoothly, but in a production cluster, pglogical replication was broken.

## Fixing Broken pglogical Replication

In the logs, we found a suspicious record regarding a missing origin:

```
ERROR:  replication origin "pgl_market_data_prod_0c0d721_sit_m6d604ee" does not exist
```

Fortunately, we were not the first ones to experience this problem. The pglogical repository 
has an [issue][1] with exactly the same problem. There, we found a solution: we needed to use 
the `pg_replication_origin_create` function to restore the missing origin.

However, the documentation and issue did not describe what an origin is and how you need to call 
this function. It took me a while to figure out how we could restore them.

To do that, I created a new replication and checked existing origins. It turns out that the origin name 
for pglogical is equal to the replication slot name.

```sql
SELECT * FROM pg_replication_origin;
```

The problem got fixed by creating origins for every replication slot of pglogical:

```sql
SELECT * FROM pg_stat_replication_slots;
SELECT pg_replication_origin_create('pgl_market_data_prod_0c0d721_sit_m6d604ee');
```

After that, the replication got restored.


[1]: https://github.com/2ndQuadrant/pglogical/issues/285
[2]: https://patroni.readthedocs.io/en/master/dcs_failsafe_mode.html
