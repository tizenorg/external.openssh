#sbs-git:slp/pkgs/o/openssh openssh 5.3p1 6697e2ccd917ab2ce8628f7b246b4bb90c93dd02
Summary: The OpenSSH implementation of SSH protocol versions 1 and 2
Name: openssh
Version: 5.3p1
Release: 2
URL: http://www.openssh.com/portable.html
Source0: openssh-%{version}.tar.gz
Source1: ssh-argv0
Source2: ssh-argv0.1
Source3: openssh-server.default
Source4: openssh-server.if-up
Source5: openssh-server.init
Source6: sshd_config
License: BSD
Group: Applications/Internet
BuildRequires: pkgconfig(zlib)
BuildRequireS: pkgconfig(openssl)
BuildRequireS: pkgconfig(libcrypto)


%package client
Summary: secure shell (SSH) client, for secure access to remote machines
Group: Applications/Internet
Requires: openssl >= 0.9.8
Provides: rsh-client, ssh-client


%package server
Summary: secure shell (SSH) server, for secure access from remote machines
Group: System/Daemons
Requires: openssh-client = %{version}-%{release}
Requires: lsb, procps
Provides: ssh-server


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
rm -rf %{buildroot}

make -C build-tmp DESTDIR=%{buildroot} install-nokeys
rm -f %{buildroot}/etc/ssh/sshd_config
rm -f %{buildroot}/usr/share/Ssh.bin

mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
mkdir -p %{buildroot}/etc/network/if-up.d

install -m 755 contrib/ssh-copy-id %{buildroot}/usr/bin/ssh-copy-id
install -m 644 -c contrib/ssh-copy-id.1 %{buildroot}/usr/share/man/man1/ssh-copy-id.1
install -m 755 %{_sourcedir}/ssh-argv0 %{buildroot}/usr/bin/ssh-argv0
install -m 644 %{_sourcedir}/ssh-argv0.1 %{buildroot}/usr/share/man/man1/ssh-argv0.1
install  %{_sourcedir}/openssh-server.init %{buildroot}/etc/init.d/ssh
install -m 644 %{_sourcedir}/openssh-server.default %{buildroot}/etc/default/ssh
install  %{_sourcedir}/openssh-server.if-up %{buildroot}/etc/network/if-up.d/openssh-server

sed -i '/\$$OpenBSD:/d' \
        %{buildroot}/etc/ssh/moduli \
        %{buildroot}/etc/ssh/ssh_config

mkdir -p %{buildroot}/etc/rc.d/init.d/
ln -s ../../init.d/ssh %{buildroot}/etc/rc.d/init.d/opensshd

install -m 600 %{_sourcedir}/sshd_config %{buildroot}/etc/ssh/sshd_config


%remove_docs

%pre server

%post server
create_key() {
        msg="$1"
        shift
        hostkeys="$1"
        shift
        file="$1"
        shift

        if echo "$hostkeys" | grep "^$file\$" >/dev/null && \
           [ ! -f "$file" ] ; then
                echo -n $msg
                ssh-keygen -q -f "$file" -N '' "$@"
                echo
                if which restorecon >/dev/null 2>&1; then
                        restorecon "$file.pub"
                fi
        fi
}


create_keys() {
        hostkeys="$(host_keys_required)"

        create_key "Creating SSH1 key; this may take some time ..." \
                "$hostkeys" /etc/ssh/ssh_host_key -t rsa1

        create_key "Creating SSH2 RSA key; this may take some time ..." \
                "$hostkeys" /etc/ssh/ssh_host_rsa_key -t rsa
        create_key "Creating SSH2 DSA key; this may take some time ..." \
                "$hostkeys" /etc/ssh/ssh_host_dsa_key -t dsa
}

create_keys


%postun server

%preun server



%files client
/etc/ssh/moduli
/etc/ssh/ssh_config
%{_bindir}/scp
%{_bindir}/sftp
%{_bindir}/slogin
%{_bindir}/ssh
%{_bindir}/ssh-*
%{_libdir}/openssh/ssh-keysign


%files server
/etc/default/ssh
/etc/init.d/ssh
/etc/network/if-up.d/openssh-server
/etc/rc.d/init.d/opensshd
/etc/ssh/sshd_config
%{_libdir}/openssh/sftp-server
%{_prefix}/sbin/sshd

