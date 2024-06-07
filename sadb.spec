Name:           sadb
Version:        0.2.1
Release:        4%{?dist}
Summary:        A package for managing apps

License:        GPL v3
URL:            https://github.com/ProjectStill/saDB
Source0:        %{url}/archive/refs/heads/main.tar.gz
BuildArch:      noarch

Requires:  python3
Requires:  python3-tqdm
Requires:  python3-click
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
mkdir -p %{buildroot}%{python3_sitelib}/sadb/source
mkdir -p %{buildroot}%{_sysconfdir}
mkdir -p %{buildroot}%{_bindir}
install -m 0755 src/__main__.py %{buildroot}%{_bindir}/sadb
install -m 0755 src/*.py %{buildroot}%{python3_sitelib}/sadb
install -m 0755 src/source/*.py %{buildroot}%{python3_sitelib}/sadb/source
install -m 0755 ex_config_files/sadb.conf %{buildroot}%{_sysconfdir}/sadb.conf

%files
%doc README.md
%license LICENSE
%dir %{python3_sitelib}/sadb
%dir %{python3_sitelib}/sadb/source
%{python3_sitelib}/sadb/source/*
%{python3_sitelib}/sadb/*
%{_sysconfdir}/sadb.conf
%{_bindir}/sadb

%changelog
* Wed May 08 2024 Cameron Knauff <cameron@stillhq.io> - 0.2.0-1
- Seperated source module
- Added installed database

* Sun Apr 14 2024 Cameron Knauff <cameron@stillhq.io> - 0.1.6-1
- Added a convenience function to get a readonly db.

* Fri Apr 12 2024 Cameron Knauff <cameron@stillhq.io> - 0.1.5-1
- Added CAUTION stillRating (0.1.5)
- Changed stillRating system to Bronze, Silver, Gold, Gold+ instead of out of 5. (0.1.4)

* Wed Apr 10 2024 Cameron Knauff <cameron@stillhq.io> - 0.1.3-1
- __main__.py is now a binary for RPM (0.1.3)
- Fixed database import in __main__.py (0.1.3)
- Added python3-tqdm as a dependency (0.1.3)
- Fixed imports (0.1.2)
- Changed sadb_classes to be part of init (idk why that wasn't there in the first place) (0.1.1)

* Mon Apr 1 2024 Cameron Knauff <cameron@stillhq.io> - 0.1-1
- First release
