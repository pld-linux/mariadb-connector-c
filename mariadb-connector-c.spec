#
%bcond_with	tests
#
Summary:	The MariaDB Native Client library (C driver)
Name:		mariadb-connector-c
Version:	3.1.11
Release:	1
License:	LGPL v2+
Group:		Libraries
Source0:	https://downloads.mariadb.org/interstitial/connector-c-%{version}/%{name}-%{version}-src.tar.gz
# Source0-md5:	cf9da5f0ac9ec72dd8309bdc1d1c6c2f
Source2:	my.cnf
Source3:	client.cnf
URL:		http://mariadb.org/
# More information: https://mariadb.com/kb/en/mariadb/building-connectorc-from-source/
Patch1:		testsuite.patch
BuildRequires:	cmake
BuildRequires:	libstdc++-devel
BuildRequires:	openssl-devel
BuildRequires:	zlib-devel
Requires:	%{_sysconfdir}/my.cnf
# Remote-IO plugin
BuildRequires:	curl-devel
# auth_gssapi_client plugin
BuildRequires:	heimdal-devel

%description
The MariaDB Native Client library (C driver) is used to connect
applications developed in C/C++ to MariaDB and MySQL databases.

%package devel
Summary:	Development files for mariadb-connector-c
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	openssl-devel
Requires:	zlib-devel

%description devel
Development files for mariadb-connector-c. Contains everything needed
to build against libmariadb.so >=3 client library.

%package test
Summary:	Testsuite files for mariadb-connector-c
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	cmake
Suggests:	mariadb-server

%description test
Testsuite files for mariadb-connector-c. Contains binaries and a
prepared CMake ctest file. Requires running MariaDB / MySQL server
with create database "test".

%package config
Summary:	Configuration files for packages that use /etc/my.cnf as a configuration file
Group:		Libraries
BuildArch:	noarch

%description config
This package delivers /etc/my.cnf that includes other configuration
files from the /etc/my.cnf.d directory and ships this directory as
well. Other packages should only put their files into /etc/my.cnf.d
directory and require this package, so the /etc/my.cnf file is
present.

%prep
%setup -q -n %{name}-%{version}-src
%patch -P1 -p1

# Remove unsused parts
rm -r win zlib win-iconv

%build
%cmake \
	-DCMAKE_SYSTEM_PROCESSOR="%{_arch}" \
	-DMARIADB_UNIX_ADDR=%{_sharedstatedir}/mysql/mysql.sock \
	-DMARIADB_PORT=3306 \
	-DWITH_EXTERNAL_ZLIB=YES \
	-DWITH_SSL=OPENSSL \
	-DWITH_MYSQLCOMPAT=ON \
	-DPLUGIN_CLIENT_ED25519=DYNAMIC \
	-DINSTALL_LAYOUT=RPM \
	-DCMAKE_INSTALL_PREFIX="%{_prefix}" \
	-DINSTALL_BINDIR="bin" \
	-DINSTALL_LIBDIR="%{_lib}" \
	-DINSTALL_INCLUDEDIR="include/mysql" \
	-DINSTALL_PLUGINDIR="%{_lib}/mariadb/plugin" \
	-DINSTALL_PCDIR="%{_lib}/pkgconfig" \
	%{?with_tests:-DWITH_UNITTEST=ON} \
	.

%{__make}

%if %{with tests}
# Check the generated configuration on the actual machine
$RPM_BUILD_ROOT%{_bindir}/mariadb_config

# Run the unit tests
# - don't run mytap tests
# - ignore the testsuite result for now. Enable tests now, fix them later.
# Note: there must be a database called 'test' created for the testcases to be run
cd unittest/libmariadb/
ctest || :
cd ../..
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# Remove static linked libraries and symlinks to them
rm $RPM_BUILD_ROOT%{_libdir}/lib*.a

# Add a compatibility symlinks
ln -s mariadb_config $RPM_BUILD_ROOT%{_bindir}/mysql_config
ln -s mariadb_version.h $RPM_BUILD_ROOT%{_includedir}/mysql/mysql_version.h

# Install config files
install -D -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/my.cnf
install -D -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/my.cnf.d/client.cnf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_libdir}/libmariadb.so.3
%dir %{_libdir}/mariadb
%dir %{_libdir}/mariadb/plugin
%attr(755,root,root) %{_libdir}/mariadb/plugin/*.so

%files devel
%defattr(644,root,root,755)
# Binary which provides compiler info for software compiling against this library
%attr(755,root,root) %{_bindir}/mariadb_config
%attr(755,root,root) %{_bindir}/mysql_config

# Symlinks to the versioned library
%attr(755,root,root) %{_libdir}/libmariadb.so
%attr(755,root,root) %{_libdir}/libmysqlclient.so
%attr(755,root,root) %{_libdir}/libmysqlclient_r.so

# Pkgconfig
%{_pkgconfigdir}/libmariadb.pc

%{_includedir}/mysql

%files config
%defattr(644,root,root,755)
%dir %{_sysconfdir}/my.cnf.d
%config(noreplace) %{_sysconfdir}/my.cnf
%config(noreplace) %{_sysconfdir}/my.cnf.d/client.cnf

%files test
%defattr(644,root,root,755)
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%attr(755,root,root) %{_libdir}/libcctap.so
