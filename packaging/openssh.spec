#sbs-git:slp/pkgs/o/openssh openssh 5.3p1 6697e2ccd917ab2ce8628f7b246b4bb90c93dd02
Name:           openssh
Version:        5.3p1
Release:        2
License:        BSD
Summary:        The OpenSSH implementation of SSH protocol versions 1 and 2
Url:            http://www.openssh.com/portable.html
Group:          Applications/Internet
Source0:        openssh-%{version}.tar.gz
Source1:        ssh-argv0
Source2:        ssh-argv0.1
Source3:        openssh-server.default
Source4:        openssh-server.if-up
Source5:        openssh-server.init
Source6:        sshd_config
Source1001:     packaging/openssh.manifest
BuildRequires:  pkgconfig(libcrypto)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(zlib)

%package client
Summary:        secure shell (SSH) client, for secure access to remote machines
Group:          Applications/Internet
Requires:       openssl >= 0.9.8
Provides:       rsh-client,
Provides:       ssh-client

%package server
Summary:        secure shell (SSH) server, for secure access from remote machines
Group:          System/Daemons
Requires:       lsb,
Requires:       openssh-client = %{version}
Requires:       procps
Provides:       ssh-server

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

%description client
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

%build
cp %{SOURCE1001} .

mkdir -p build-tmp
cd build-tmp

../configure \
        --prefix=/usr --sysconfdir=/etc/ssh \
        --libexecdir=/usr/lib/openssh \
        --mandir=/usr/share/man \
        --disable-strip --with-mantype=doc --with-4in6 \
        --with-privsep-path=/var/run/sshd --without-rand-helper \
        --without-xauth \
        --with-default-path=/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/games \
        --with-superuser-path=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/bin/X11 \
        --with-cflags='-O2   -DLOGIN_PROGRAM=\"/bin/login\" -DLOGIN_NO_ENDOPT ' \
        --with-ldflags='-Wl,--as-needed'

make -C . -j 2 ASKPASS_PROGRAM='/usr/bin/ssh-askpass'



%install

make -C build-tmp DESTDIR=%{buildroot} install-nokeys
rm -f %{buildroot}%{_sysconfdir}/ssh/sshd_config
rm -f %{buildroot}%{_datadir}/Ssh.bin

mkdir -p %{buildroot}%{_sysconfdir}/init.d
mkdir -p %{buildroot}%{_sysconfdir}/default
mkdir -p %{buildroot}%{_sysconfdir}/network/if-up.d

install -m 755 contrib/ssh-copy-id %{buildroot}%{_bindir}/ssh-copy-id
install -m 644 -c contrib/ssh-copy-id.1 %{buildroot}%{_mandir}/man1/ssh-copy-id.1
install -m 755 %{_sourcedir}/ssh-argv0 %{buildroot}%{_bindir}/ssh-argv0
install -m 644 %{_sourcedir}/ssh-argv0.1 %{buildroot}%{_mandir}/man1/ssh-argv0.1
install  %{_sourcedir}/openssh-server.init %{buildroot}%{_initddir}/ssh
install -m 644 %{_sourcedir}/openssh-server.default %{buildroot}%{_sysconfdir}/default/ssh
install  %{_sourcedir}/openssh-server.if-up %{buildroot}%{_sysconfdir}/network/if-up.d/openssh-server

sed -i '/\$$OpenBSD:/d' \
        %{buildroot}%{_sysconfdir}/ssh/moduli \
        %{buildroot}%{_sysconfdir}/ssh/ssh_config

mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d/
ln -s ../../init.d/ssh %{buildroot}%{_sysconfdir}/rc.d/init.d/opensshd

install -m 600 %{_sourcedir}/sshd_config %{buildroot}%{_sysconfdir}/ssh/sshd_config


%remove_docs


%files client
%manifest openssh.manifest
%{_sysconfdir}/ssh/moduli
%{_sysconfdir}/ssh/ssh_config
%{_bindir}/scp
%{_bindir}/sftp
%{_bindir}/slogin
%{_bindir}/ssh
%{_bindir}/ssh-*
%{_libdir}/openssh/ssh-keysign


%files server
%manifest openssh.manifest
%{_sysconfdir}/default/ssh
%{_sysconfdir}/init.d/ssh
%{_sysconfdir}/network/if-up.d/openssh-server
%{_sysconfdir}/rc.d/init.d/opensshd
%{_sysconfdir}/ssh/sshd_config
%{_libdir}/openssh/sftp-server
%{_sbindir}/sshd

