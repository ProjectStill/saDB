Name:           sadb
Version:        0.1.1
Release:        1%{?dist}
Summary:        A package for managing apps

License:        GPL v3
URL:            https://github.com/ProjectStill/saDB
Source0:        %{url}/archive/refs/heads/main.tar.gz
BuildArch:      noarch

Requires:  python3
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

%description
saDB is a solution for managing app sources and databases for stillOS.
When paired with stillAppMan, it can be used by distro vendors to moderate
apps from third party sources without maintaining their own repos.

%prep
%autosetup -n saDB-main

%build
%install
mkdir -p %{buildroot}%{python3_sitelib}/sadb
mkdir -p %{buildroot}%{_sysconfdir}
install -m 0755 src/* %{buildroot}%{python3_sitelib}/sadb
install -m 0755 ex_config_files/sadb.conf %{buildroot}%{_sysconfdir}/sadb.conf

%files
%doc README.md
%license LICENSE
%dir %{python3_sitelib}/sadb
%{python3_sitelib}/sadb/*
%{_sysconfdir}/sadb.conf

%changelog
* Wed Apr 1 2024 Cameron Knauff <cameron@stillhq.io> - 0.1-1
- First release
