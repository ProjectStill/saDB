Name:           sadb
Version:        0.1.4
Release:        1%{?dist}
Summary:        A package for managing apps

License:        GPL v3
URL:            https://github.com/ProjectStill/saDB
Source0:        %{url}/archive/refs/heads/main.tar.gz
BuildArch:      noarch

Requires:  python3
Requires:  python3-tqdm
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
mkdir -p %{buildroot}%{_bindir}
install -m 0755 src/__main__.py %{buildroot}%{_bindir}/sadb
install -m 0755 src/* %{buildroot}%{python3_sitelib}/sadb
install -m 0755 ex_config_files/sadb.conf %{buildroot}%{_sysconfdir}/sadb.conf

%files
%doc README.md
%license LICENSE
%dir %{python3_sitelib}/sadb
%{python3_sitelib}/sadb/*
%{_sysconfdir}/sadb.conf
%{_bindir}/sadb

%changelog
* Fri Apr 12 2024 Cameron Knauff <cameron@stillhq.io> - 0.1.4-1
- Changed stillRating system to Bronze, Silver, Gold, Gold+ instead of out of 5.

* Wed Apr 10 2024 Cameron Knauff <cameron@stillhq.io> - 0.1.3-1
- __main__.py is now a binary for rpms (0.1.3)
- Fixed database import in __main__.py (0.1.3)
- Added python3-tqdm as a dependency (0.1.3)
- Fixed imports (0.1.2)
- Changed sadb_classes to be part of init (idk why that wasn't there in the first place) (0.1.1)

* Wed Apr 1 2024 Cameron Knauff <cameron@stillhq.io> - 0.1-1
- First release
