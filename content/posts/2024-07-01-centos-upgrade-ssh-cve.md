---
title: "CentOS: Fix CVE-2024-6387 by Updating OpenSSH"
description: "A step-by-step guide to upgrading OpenSSH on CentOS to mitigate CVE-2024-6387"
tags: ["CVE", "CentOS", "Linux"]
date: 2024-07-01
slug: "centos-upgrade-ssh-cve"
---

# Introduction

CVE-2024-6387, a recently discovered vulnerability, allows for remote code execution (RCE) on affected servers running OpenSSH versions. Given CentOS is deprecated, this guide details how to upgrade to the latest versions of OpenSSL and OpenSSH to mitigate this risk.

## Affected OpenSSH versions

* OpenSSH versions earlier than 4.4p1 are vulnerable to this signal handler race condition unless they are patched for CVE-2006-5051 and CVE-2008-4109.
* Versions from 4.4p1 up to, but not including, 8.5p1 are not vulnerable due to a transformative patch for CVE-2006-5051, which made a previously unsafe function secure.
* The vulnerability resurfaces in versions from 8.5p1 up to, but not including, 9.8p1 due to the accidental removal of a critical component in a function.

# Installation Steps

## Install Dependencies

First, install the necessary development tools and libraries:

```shell
yum groupinstall -y "Development Tools"
yum install -y wget perl coreutils perl-IPC-Cmd perl-Data-Dumper pam-devel
```

## Backup Existing OpenSSL

Backup the current OpenSSL to avoid conflicts:

```shell
mv /usr/bin/openssl /usr/bin/openssl_backup
```

## Install Latest OpenSSL


Check for the latest version on the [OpenSSL website](https://www.openssl.org/source/). For this guide, we use version `3.3.1`:

```shell
OPENSSL_VERSION="3.3.1"

wget https://www.openssl.org/source/openssl-$OPENSSL_VERSION.tar.gz
tar -zxvf openssl-$OPENSSL_VERSION.tar.gz
cd openssl-$OPENSSL_VERSION
./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl shared zlib
make
make install

# Update the system OpenSSL to the new version
echo "/usr/local/openssl/lib" > /etc/ld.so.conf.d/openssl.conf
ldconfig
ln -sf /usr/local/openssl/bin/openssl /usr/bin/openssl
ln -s /usr/local/openssl/lib64/libssl.so.3 /usr/lib64/
ln -s /usr/local/openssl/lib64/libcrypto.so.3 /usr/lib64/
openssl version -a
```

## Install Latest OpenSSH

First, backup the existing OpenSSH configuration:

```shell
mkdir /etc/ssh_old
mv /etc/ssh/* /etc/ssh_old/
```

Then, download and install the [latest OpenSSH](https://github.com/openssh/openssh-portable/tags) version (`9.8p1` for this guide):

```shell
OPENSSH_VERSION="9.8p1"
wget https://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-$OPENSSH_VERSION.tar.gz
tar -zxvf openssh-$OPENSSH_VERSION.tar.gz
cd openssh-$OPENSSH_VERSION

# Configure OpenSSH with the new OpenSSL
./configure --prefix=/usr --sysconfdir=/etc/ssh --with-ssl-dir=/usr/local/openssl --with-zlib --with-ssl-engine --with-pam
make
make install
```

Verify the installation:

```
ssh -V
# OpenSSH_9.8p1, OpenSSL 3.3.1 4 Jun 2024
```

## Update Configuration
Compare the old and new SSH configuration files:

```shell
diff /etc/ssh/sshd_config /etc/ssh_old/sshd_config
# Edit the new one if needed
vim /etc/ssh/sshd_config
```

Replace the SSH daemon service files:

```shell
mv /usr/lib/systemd/system/sshd.service /etc/ssh_old/sshd.service
mv /usr/lib/systemd/system/sshd.socket /etc/ssh_old/sshd.socket
cp -a contrib/redhat/sshd.init /etc/init.d/sshd

systemctl daemon-reload
systemctl restart sshd

chkconfig --add sshd
chkconfig sshd on
```

## Testing the New Configuration

Finally, test the new SSH setup by connecting to the server using the `-vv` flag to verify the protocol version in use.

```shell
ssh -vv user@your-server.com
```

Stay secure!