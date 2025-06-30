---
title: "Use AWS SSO as ABAC IAM for granular secure access"
description: "Learn how to implement ABAC with AWS SSO and your Identity Provider"
tags: ["AWS", "SSO", "ABAC", "IAM"]
date: 2025-06-30
slug: "aws-iam-sso-abac"
tldr: |
  How to configure AWS SSO and your IdP to pass custom tags into an assumed role session to compare them at the IAM policy level.
  This is useful for limiting a developer's role to team-based database instances.
---

## Intro
Most security teams want to limit developers' access to only their own resources in AWS. This is especially true for databases.
Previously, we solved this by creating multiple IAM roles, where users would choose the appropriate role to access specific cloud resources.
This works fine on a small scale, but doesn't scale beyond 3+ roles or teams.

Instead, we can use attribute-based access control (ABAC) to compare user properties with resource tags and determine access permissions.

I decided to write this article because I couldn't find a guide on how to do it. The [AWS Doc][1] is quite limited.

## AWS SAML vs AWS SSO

The AWS SAML auth provider linked with an IAM role has many more capabilities for SAML attributes and is [well-documented][2].

AWS SSO has limited functionality and does not support:
- Multi-valued SAML attributes
- `TransitiveTagKeys`

To pass attributes from an IdP via SAML to an assumed session's `PrincipalTag`, you can use only `https://aws.amazon.com/SAML/Attributes/AccessControl:<name>` with string-typed values up to 460 bytes long.

We use `::` as a separator for concatenating multiple values and `:` as a logical separator within individual entities.

## Schema

Authentication and authorization flow:
![diag](./diag-1.svg)

{{< details "Diagram source" >}}
```mermaid
sequenceDiagram
    participant User
    participant AWS_SSO as AWS SSO
    participant IDP
    participant Target_AWS_Account as Target AWS Account

    User->>AWS_SSO: Initiates Login
    AWS_SSO->>IDP: Redirects user for authentication (SAML Request)
    IDP-->>User: Login Page
    User->>IDP: Enters Credentials
    IDP->>AWS_SSO: SAML Assertion with<br/>AccessControl attributes
    AWS_SSO->>Target_AWS_Account: AssumeRoleWithSAML
    Target_AWS_Account-->>AWS_SSO: Assumed Role Session<br/>with principal tags
    AWS_SSO-->>User: Grants access to AWS Account
```
{{< /details >}}

## IdP

To configure role attributes, we'll use Authentik (our SAML identity provider) that's already configured with AWS SSO.
The first step is to create the `Property Mappings`.

![mappings](./mappings.png)

```python
attributes_list = request.user.group_attributes().get("security:authz:groups", [])
unique_attributes_set = set(attributes_list)

return "::".join(unique_attributes_set)
```

This code collects properties from the user's assigned groups, deduplicates them, and concatenates the results using `::`.

After configuring the property mappings, log out of AWS SSO and log back in to test the configuration.

{{< inline_img src="logout.png" alt="logout" >}}

You should see a new record for `AssumeRoleWithSAML` in your CloudTrail events. The `principalTags` from this event can be used in IAM conditions.

```json
{
  "requestParameters": {
      "sAMLAssertionID": "_550580ed-e988-46da-bebd-38d9bcd1f156",
      "roleSessionName": "XXXXX@qdo.ee",
      "principalTags": {
          "security:authz:dbusers": "beta:developer-iam::prod-us:developer-iam",
          "security:authz:groups": "beta:pfr:project::any:rpsql:project"
      }
}
```


### IAM

As mentioned in the beginning, to limit developers to certain resources in their domain of responsibility, we'll match the passed `aws:PrincipalTag/security:authz:groups` with a regexp formed from the `ResourceTag` assigned to the database:

```
    condition {
      test = "StringLike"
      values = flatten([
        [for env in var.allowed_environment : "*${env}:$${ssm:ResourceTag/security:access:st}:$${ssm:ResourceTag/security:access:group}*"],
        ["*any:$${ssm:ResourceTag/security:access:st}:$${ssm:ResourceTag/security:access:group}*"]
      ])

      variable = "aws:PrincipalTag/security:authz:groups"
    }
```

[1]: https://docs.aws.amazon.com/singlesignon/latest/userguide/attributesforaccesscontrol.html
[2]: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_saml_assertions.html
