Name:           openssh
Version:        5.6p1
Release:        1
%define sshd_uid    74
%define sshd_gid    74
Summary:        The OpenSSH implementation of SSH protocol versions 1 and 2
Url:            http://www.openssh.com/portable.html
Source0:        openssh-%{version}.tar.bz2
Source1:        openssh-nukeacss.sh
Source4:        sshd.service
Source5:        sshd@.service
Source6:        sshd.socket
Source7:        sshd-keys.service
Source8:        sshd-hostkeys
Source1001:     openssh.manifest

Patch0:         0001-customize-configuration.patch
Patch1:         0002-log-in-chroot.patch
Patch2:         0003-rand-clean.patch
Patch3:         0004-big-uid.patch
Patch4:         0005-client-loop.patch
Patch5:         0006-CVE-2010-4478.patch
Patch6:         0007-Do-not-put-ssh-keys-in-etc.patch

License:        BSD
Group:          Applications/Internet

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  nss-devel
BuildRequires:  perl
BuildRequires:  util-linux
BuildRequires:  xauth
BuildRequires:  zlib-devel
BuildRequires:  pkgconfig(ncurses)
BuildRequires:  pkgconfig(openssl)

%package clients
Summary:        The OpenSSH client applications
Group:          Applications/Internet
Requires:       openssh = %{version}

%package server
Summary:        The OpenSSH server daemon
Group:          System/Daemons
Requires:       openssh = %{version}
Requires(pre): /usr/sbin/useradd


%description
SSH (Secure SHell) is a program for logging into and executing
commands on a remote machine. SSH is intended to replace rlogin and
rsh, and to provide secure encrypted communications between two
untrusted hosts over an insecure network. X11 connections and
arbitrary TCP/IP ports can also be forwarded over the secure channel.

OpenSSH is OpenBSD's version of the last free version of SSH, bringing
it up to date in terms of security and features, as well as removing
all patented algorithms to separate libraries.

This package includes the core files necessary for both the OpenSSH
client and server. To make this package useful, you should also
install openssh-clients, openssh-server, or both.

%description clients
OpenSSH is a free version of SSH (Secure SHell), a program for logging
into and executing commands on a remote machine. This package includes
the clients necessary to make encrypted connections to SSH servers.
You'll also need to install the openssh package on OpenSSH clients.

%description server
OpenSSH is a free version of SSH (Secure SHell), a program for logging
into and executing commands on a remote machine. This package contains
the secure shell daemon (sshd). The sshd daemon allows SSH clients to
securely connect to your SSH server. You also need to have the openssh
package installed.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
cp %{S:1001} .

CFLAGS="%{optflags}"; export CFLAGS
CFLAGS="$CFLAGS -fpie"
export CFLAGS
LDFLAGS="$LDFLAGS -pie"; export LDFLAGS

%reconfigure \
	--sysconfdir=%{_sysconfdir}/ssh \
	--libexecdir=%{_libexecdir}/openssh \
	--datadir=%{_datadir}/openssh \
	--with-rsh=%{_bindir}/rsh \
	--with-default-path=/usr/local/bin:/bin:/usr/bin \
	--with-superuser-path=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin \
	--with-privsep-path=%{_localstatedir}/empty/sshd \
	--enable-vendor-patchlevel="FC-%{version}-%{release}" \
	--disable-strip \
	--without-zlib-version-check \
	--with-nss \
    	--without-kerberos5

make

%install
mkdir -p -m755 %{buildroot}%{_sysconfdir}/ssh
mkdir -p -m755 %{buildroot}%{_libexecdir}/openssh
mkdir -p -m755 %{buildroot}%{_localstatedir}/empty/sshd

%make_install
rm -f %{buildroot}%{_sysconfdir}/ssh/ldap.conf

install -d %{buildroot}%{_libexecdir}/openssh
install -m755 contrib/ssh-copy-id %{buildroot}%{_bindir}/

# systemd integration
install -D -m 0644 %{SOURCE4} %{buildroot}/%{_lib}/systemd/system/sshd.service
install -D -m 0644 %{SOURCE5} %{buildroot}/%{_lib}/systemd/system/sshd@.service
install -D -m 0644 %{SOURCE6} %{buildroot}/%{_lib}/systemd/system/sshd.socket
install -D -m 0644 %{SOURCE7} %{buildroot}/%{_lib}/systemd/system/sshd-keys.service
mkdir -p %{buildroot}/%{_lib}/systemd/system/multi-user.target.wants
ln -s ../sshd.socket %{buildroot}/%{_lib}/systemd/system/multi-user.target.wants/sshd.socket
install -D -m 0755 %{SOURCE8} %{buildroot}%{_sbindir}/sshd-hostkeys
mkdir -p %{buildroot}/%{_lib}/systemd/system/multi-user.target.wants
ln -s ../sshd-keys.service %{buildroot}/%{_lib}/systemd/system/multi-user.target.wants/sshd-keys.service

rm -f %{buildroot}%{_sysconfdir}/profile.d/gnome-ssh-askpass.*

%remove_docs

rm -rf %{buildroot}%{_datadir}/man

%triggerun server -- ssh-server
if [ "$1" != 0 -a -r /var/run/sshd.pid ] ; then
	touch /var/run/sshd.restart
fi

%pre server
/usr/sbin/useradd -c "Privilege-separated SSH" -u %{sshd_uid} \
	-s /bin/false -r -d /var/empty/sshd sshd 2> /dev/null || :



%files
%manifest openssh.manifest
%attr(0755,root,root) %dir %{_sysconfdir}/ssh
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/ssh/moduli

%attr(0755,root,root) %{_bindir}/ssh-keygen
%attr(0755,root,root) %dir %{_libexecdir}/openssh
%attr(4755,root,root) %{_libexecdir}/openssh/ssh-keysign

%files clients
%manifest openssh.manifest
%attr(0755,root,root) %{_bindir}/ssh
%attr(0755,root,root) %{_bindir}/scp
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ssh/ssh_config
%attr(0755,root,root) %{_bindir}/slogin
%attr(2755,root,nobody) %{_bindir}/ssh-agent
%attr(0755,root,root) %{_bindir}/ssh-add
%attr(0755,root,root) %{_bindir}/ssh-keyscan
%attr(0755,root,root) %{_bindir}/sftp
%attr(0755,root,root) %{_bindir}/ssh-copy-id
%attr(0755,root,root) %{_libexecdir}/openssh/ssh-pkcs11-helper

%files server
%manifest openssh.manifest
%dir %attr(0711,root,root)
%attr(0755,root,root) %{_sbindir}/sshd
%attr(0755,root,root) %{_libexecdir}/openssh/sftp-server
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/ssh/sshd_config
/%{_lib}/systemd/system/sshd.service
/%{_lib}/systemd/system/sshd.socket
/%{_lib}/systemd/system/sshd@.service
/%{_lib}/systemd/system/sshd-keys.service
/%{_lib}/systemd/system/multi-user.target.wants/sshd.socket
/%{_lib}/systemd/system/multi-user.target.wants/sshd-keys.service
%{_sbindir}/sshd-hostkeys

