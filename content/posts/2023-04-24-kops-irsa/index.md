---
title: "Enabling IRSA for ServiceAccounts in Kops"
description: |
  Learn from my experience on how to enable IRSA (IAM Roles for ServiceAccounts)
  support in Kops managed clusters, and leverage AWS authentication and authorization
  for your applications.
tags: []
date: 2023-04-24
slug: "kops-irsa"
thumbnail: ./art-cover.png
resources:
- src: ./art-cover.png
---

![image](./art-cover.png)

When I first started looking into adding IRSA (IAM Roles for ServiceAccounts) support to my
Kops managed Kubernetes clusters, I found [the documentation][1] to be extremely confusing. 
I wanted to share my journey and the steps I took to successfully enable IRSA support, 
configure my cluster, and test the setup.

I decided to do that because we faced the [same issue][2] as described in Kiam repo
with random `502` errors for `/latest/api/token` endpoint which broke our pipeline.

### Prerequisites

Before diving into my story, make sure you have the following:

1. A Kops managed Kubernetes cluster
2. Terraform installed and configured to manage Kops state

### Enable OIDC and face the dots dilemma

The first step was to configure the `serviceAccountIssuerDiscovery` section in Kops 
cluster configuration.

Dots in S3 bucket names are widely used in our terraform modules, to add Java style prefixes
like `ee.hdo.beta.`. I wanted to use the same approach for OIDC public bucket, which was
a bit puzzling at first.
The reason is that IRSA relies on the OpenID Connect (OIDC) discovery endpoint, and dots
in the hostname can cause potential issues with SSL certificate validation.

```yaml
  serviceAccountIssuerDiscovery:
    discoveryStore: s3://ee.hdo.beta.irsa.providers
    enableAWSOIDCProvider: true
```

error was displayed in yaml file header:

```yaml
# error populating cluster spec: spec.serviceAccountIssuerDiscovery.serviceAccountIssuerDiscovery.discoveryStore: Invalid value: "s3://ee.hdo.beta.irsa.providers": Bucket name cannot contain dots
```

I ended up with the next configuration:

```yaml
  serviceAccountIssuerDiscovery:
    discoveryStore: s3://hdo-beta-irsa-providers
    enableAWSOIDCProvider: true
```

Important to notice that bucket shouldn't block public access.

`serviceAccountIssuerDiscovery` configuration enables trust relation between AWS IAM
and certificate issued by Kops. For that, kops require having a publicly available store.
Previously issued keys that were used by kops originally replaced with new one. Public part of it
we will store in S3.

This way tokens that are stored in SA secrets can be validated by external agent, AWS in our case
using the asymmetrical JWT key pair.


Keep in mind that enabling `serviceAccountIssuerDiscovery` in runtime will cause all SA to regenerate
[their secrets][1].

> Warning: Enabling the following configuration on an existing cluster can be disruptive due to the 
> control plane provisioning tokens with different issuers. The symptom is that Pods are unable to 
> authenticate to the Kubernetes API. To resolve this, delete Service Account token secrets that exists 
> in the cluster and kill all pods unable to authenticate.

```yaml
      -     serviceAccountIssuer: https://api.internal.k8s.beta.hdo.ee
      -     serviceAccountJWKSURI: https://api.internal.k8s.beta.hdo.ee/openid/v1/jwks
      +     serviceAccountIssuer: https://hdo-beta-irsa-providers.s3.eu-west-1.amazonaws.com
      +     serviceAccountJWKSURI: https://hdo-beta-irsa-providers.s3.eu-west-1.amazonaws.com/openid/v1/jwks
```

### Dealing with cert-manager

Next, I needed to enable `certManager` in my Kops cluster configuration. However, I was already 
managing `cert-manager` using Helm, so I set the `managed` field to `false`.

```yaml
  serviceAccountIssuerDiscovery:
    discoveryStore: s3://hdo-beta-irsa-providers
    enableAWSOIDCProvider: true
  certManager:
    enabled: true
    managed: false
```

### The `podIdentityWebhook` magic

I then enabled the `podIdentityWebhook` in my Kops cluster configuration. 
That service registers a webhook to [mutate][3] pods, by adding environment variables necessary 
for assuming IAM roles.

```yaml
  serviceAccountIssuerDiscovery:
    discoveryStore: s3://hdo-beta-irsa-providers
    enableAWSOIDCProvider: true
  certManager:
    enabled: true
    managed: false
  podIdentityWebhook:
    enabled: true
```

### Enabling IRSA for managed addons

By default, kops adds additional permissions to the node roles; instead it can use
dedicated roles attached to SA.

```yaml
  iam:
    useServiceAccountExternalPermissions: true
  serviceAccountIssuerDiscovery:
    discoveryStore: s3://hdo-beta-irsa-providers
    enableAWSOIDCProvider: true
  certManager:
    enabled: true
    managed: false
  podIdentityWebhook:
    enabled: true
```

### Updating the cluster and applying changes

With my Kops configuration complete, I updated the terraform code:
```bash
kops update cluster --target=terraform --out=update --yes
```

I carefully checked the diff between the update folder and my Terraform
content before applying the changes using `terraform apply`.

### Rotating control plane nodes

After applying the Terraform state to the target cluster, I rotated the
control plane nodes by draining them. This was crucial because enabling
`serviceAccountIssuerDiscovery` caused all `ServiceAccounts` to regenerate their tokens.

Since SA is invalid, `aws-iam-authenticator` isn't working anymore. 
This is because the tokens generated by the new service account issuer aren't compatible 
with the previous aws-iam-auth configuration.

You need to issue static credentials to access the cluster:

```bash
kops export kubeconfig --auth-plugin --admin=5h
```

After that you need to delete all Secrets with a type `service-account` and then delete pods.

```bash
kubectl get secrets -A -o json \
| jq '.items[] | select(.type=="kubernetes.io/service-account-token") | "kubectl delete secret \(.metadata.name) -n \(.metadata.namespace)"' \
| xargs -n 1 bash -c
```

Next, delete all the pods to force their recreation with the new service account tokens:
```bash 
kubectl get pods --all-namespaces \
| grep -v 'NAMESPACE' \
| awk '{print $1" "$2}' \
| xargs -n 2 bash -c 'kubectl delete pod -n $0 $1'
```

You may delete only selected pods if deleting all of them is too disruptive for your cluster.

After running these commands, your cluster will begin recreating the pods with the new service account tokens, and they should be able to authenticate using IRSA.

### Configuring IAM trust

All activities with the cluster are done, and I started adopting IAM roles to trust new OIDC
provider.

To make sure that your role trust created OIDC, you need to add additional trust policy to it:

```terraform
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }
    condition {
      variable = "${replace(var.oidc_provider_arn, "/^(.*provider/)/", "")}:sub"
      values   = [for sa in module.configuration.trusted_sa : "system:serviceaccount:${sa}"]
      test     = "StringEquals"
    }
    # :aud is not added because it works only with EKS
  }
```

`trusted_sa` is an array of strings with concatenated `namespace:sa_name`.

{{< details "Full code of the Terraform role creation" >}}

```terraform
resource "aws_iam_role" "this" {
  name               = var.name
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json

  tags = {
    Terraform = true
  }
}

data "aws_iam_policy_document" "assume_role_policy" {
  # Preserve legacy trust policy for the migration period
  statement {
    actions = ["sts:AssumeRole"]

    dynamic "principals" {
      for_each = module.configuration.identifiers

      content {
        type        = principals.key
        identifiers = principals.value
      }
    }
  }

  # Trust to the SA if they are configured
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }

    condition {
      variable = "${replace(var.oidc_provider_arn, "/^(.*provider/)/", "")}:sub"
      values   = [for sa in module.configuration.trusted_sa : "system:serviceaccount:${sa}"]
      test     = "StringEquals"
    }

    # :aud is not added because it works only with EKS
    #    # https://aws.amazon.com/premiumsupport/knowledge-center/eks-troubleshoot-oidc-and-irsa/?nc1=h_ls
    #    condition {
    #      variable = "${replace(var.oidc_provider_arn, "/^(.*provider/)/", "")}:aud"
    #      values   = ["sts.amazonaws.com"]
    #      test     = "StringEquals"
    #    }
  }
}
```
{{< /details >}}

### Testing the setup

To test that your SA with the assigned role via `eks.amazonaws.com/role-arn` annotation works as expected
you can run a debug pod with mounted SA. Found in [gist][5]. 

```bash
kubectl run --rm -it debug --image amazon/aws-cli --command bash --overrides='{ "spec": { "serviceAccount": "my-cool-service-account" }  }'
```

Then call default sts method to verify the assumed role:

```bash
aws sts get-caller-identity
```

### Additional information

To get a better understanding of how IRSA works in general, you may check incredible [article][7].
It explains in an easy graphical form how trust relations works and why this way of granting permissions
is better than `Kiam` or `Kube2iam`

### Post migration

We're planning to migrate our workloads to use IRSA via mounted ServiceAccounts.
After that we will enforce IMDSv2 with hop limit set to `1`.
That will help us to protect instance attached roles from being used by pods deployed to the same machine.

Pods with `hostNetwork` will be denied by gatekeeper to enforce the security policy.

[1]: https://kops.sigs.k8s.io/cluster_spec/#service-account-issuer-discovery-and-aws-iam-roles-for-service-accounts-irsa
[2]: https://github.com/uswitch/kiam/issues/398
[3]: https://github.com/aws/amazon-eks-pod-identity-webhook
[4]: https://kops.sigs.k8s.io/cluster_spec/#iam-roles-for-addons
[5]: https://gist.github.com/aramse/6eb4a5b11269bb19d9ad35bb21ace6f6
[6]: https://repost.aws/knowledge-center/eks-troubleshoot-oidc-and-irsa
[7]: https://medium.com/@ankit.wal/the-how-of-iam-roles-for-service-accounts-irsa-on-aws-eks-3d76badb8942
[8]: https://aws.amazon.com/blogs/opensource/introducing-fine-grained-iam-roles-service-accounts/
