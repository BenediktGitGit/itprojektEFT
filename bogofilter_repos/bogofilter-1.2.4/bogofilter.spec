# $Id: bogofilter.spec.in 6431 2006-01-22 03:28:21Z relson $

# This .spec file will not build the static package by default.
# To do this, run either of the next rpm[build] commands:
#
# rpmbuild --define 'bogostatic 1' --sign -bb bogofilter.spec
#
# To build with SQLite3, use:
#
# rpmbuild --define 'with_sqlite 1' --sign -bb bogofilter.spec

# To build -debuginfo RPMs on systems with RPM 4.2 or newer and recent
# elfutils, add
#
# --define 'debugrpm 1'
#
# or place   %debugrpm 1   into your ~/.rpmmacros file.

%define	Name		bogofilter
%define	Version		1.2.4
%define	Release		1

%{?bogostatic:  %define bogostatic 1}
%{!?bogostatic: %define bogostatic 0}

%{?with_db42:   %define with_db42 1}
%{!?with_db42:  %define with_db42 0}

%{?with_sqlite:  %define with_sqlite 1}
%{!?with_sqlite: %define with_sqlite 0}

%if %{with_db42}
%define DBFlag 1
%define DBName -db42
%endif

%if %{with_sqlite}
%define DBFlag 1
%define DBName -sqlite3
%endif

%{!?DBFlag: %define DBFlag 0}
%{!?bf_nameext: %define bf_nameext %{nil}}

Summary:	Fast anti-spam filtering by Bayesian statistical analysis
%if ! %{DBFlag}
Name:		%{Name}%{bf_nameext}
%else
Name:		%{Name}%{DBName}%{bf_nameext}
%endif
Version:	%{Version}
Release:	%{Release}
License:	GPL
Group:		Networking/Mail
URL:		http://bogofilter.sourceforge.net
Source0:	%{Name}-%{Version}.tar.gz

%define _requires_exceptions perl

Buildroot:	%{_tmppath}/%{Name}-%{Version}-root
Conflicts:	%{Name}%{DBName}-static

%description
Bogofilter is a Bayesian spam filter.  In its normal mode of
operation, it takes an email message or other text on standard input,
does a statistical check against lists of "good" and "bad" words, and
returns a status code indicating whether or not the message is spam.
Bogofilter is designed with fast algorithms (including Berkeley DB system),
coded directly in C, and tuned for speed, so it can be used for production
by sites that process a lot of mail.

%if %{with_sqlite}
This version was built with SQLite3 support.
%else
This version was built with Berkeley DB support.
%endif

%package static
Summary:	Statically linked
Group:		Networking/Mail
Conflicts:	%{Name}%{DBName}

%description static
Statically linked bogofilter, bogolexer, bogoutil, and bogotune.

# use the debug_package macro if applicable:
%{?debugrpm:%debug_package}

%prep
%setup -q -n %{Name}-%{Version}
CFLAGS="$RPM_OPT_FLAGS" \
./configure \
  --prefix=%{_prefix} \
  --mandir=%{_mandir} \
  --sysconfdir=%{_sysconfdir} \
%if %{?bogostatic}
  --enable-static \
%endif
%if %{?with_db42}
  --with-database=db \
%endif
%if %{?with_sqlite}
  --with-database=sqlite3 \
%endif
  --with-included-gsl

%build
make
make DESTDIR="%{buildroot}" check

%clean
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

cp %{buildroot}%{_sysconfdir}/bogofilter.cf.example \
   %{buildroot}%{_sysconfdir}/bogofilter.cf

for n in xml html ; do
  install -d .inst/$n
  install -m644 doc/*.$n .inst/$n
done

for n in `find %{buildroot}%{_datadir}/%{name} -type d` ; do
  chmod o-w $n
done

for d in contrib ; do
  install -d %{buildroot}%{_datadir}/%{name}/$d
  files=$(find "$d" -maxdepth 1 -type f -print)
  for f in $files ; do
    case $f in
      *.c|*.o|*.obj|*/Makefile*) continue ;;
      *.1)
	cp -p $f %{buildroot}%{_mandir}/man1 ;;
      *)
	cp -p $f %{buildroot}%{_datadir}/%{name}/$d ;;
    esac
  done
done

mv bogogrep* contrib

%if %{bogostatic}
(
cd %{buildroot}%{_datadir}/%{name}
cp -p -r contrib contrib-static
rm contrib/bogogrep_static
rm contrib-static/bogogrep
strip contrib-static/bogogrep_static
)
%endif

%post

%post static
for file in bogofilter bogolexer bogoutil bogotune ; do
    if [ $1 -lt 2 ] ; then
        ln -s %{_bindir}/${file}_static %{_bindir}/${file} 
    fi
done

%postun static
for file in bogofilter bogolexer bogoutil bogotune ; do
    if [ $1 -eq 0 ] ; then
        rm -f %{_bindir}/${file}
        echo rm -f %{_bindir}/${file}
    fi
done

%files
%defattr(-,root,root)

%doc AUTHORS COPYING INSTALL
%doc GETTING.STARTED
%doc NEWS README* RELEASE.NOTES TODO
%doc doc/bogofilter-tuning.HOWTO.html
%doc doc/bogofilter-SA-2002-01
%doc doc/integrating*
%doc doc/programmer
%doc doc/README.*db doc/rpm.notes.BerkeleyDB
%doc .inst/html .inst/xml

%{_sysconfdir}/bogofilter.cf.example
%config(noreplace) %{_sysconfdir}/bogofilter.cf

%{_bindir}/bogofilter
%{_bindir}/bogolexer
%{_bindir}/bogotune
%{_bindir}/bogoutil
%{_bindir}/bogoupgrade
%{_bindir}/bf_copy
%{_bindir}/bf_compact
%{_bindir}/bf_tar

%{_mandir}/man1/bogofilter.1*
%{_mandir}/man1/bogolexer.1*
%{_mandir}/man1/bogotune.1*
%{_mandir}/man1/bogoutil.1*
%{_mandir}/man1/bogoupgrade.1*
%{_mandir}/man1/bf_compact.1*
%{_mandir}/man1/bf_copy.1*
%{_mandir}/man1/bf_tar.1*

%{_datadir}/%{name}/contrib/*

%if %{bogostatic}
%files static
%defattr(-,root,root)

%doc AUTHORS COPYING INSTALL
%doc GETTING.STARTED
%doc NEWS README* RELEASE.NOTES TODO
%doc doc/bogofilter-tuning.HOWTO.html
%doc doc/bogofilter-SA-2002-01
%doc doc/integrating*
%doc doc/programmer
%doc doc/README.*db doc/rpm.notes.BerkeleyDB
%doc .inst/html .inst/xml

%{_sysconfdir}/bogofilter.cf.example
%config(noreplace) %{_sysconfdir}/bogofilter.cf

%{_bindir}/bogofilter_static
%{_bindir}/bogolexer_static
%{_bindir}/bogotune_static
%{_bindir}/bogoutil_static
%{_bindir}/bogoupgrade
%{_bindir}/bf_copy
%{_bindir}/bf_compact
%{_bindir}/bf_tar

%{_mandir}/man1/bogofilter.1*
%{_mandir}/man1/bogolexer.1*
%{_mandir}/man1/bogotune.1*
%{_mandir}/man1/bogoutil.1*
%{_mandir}/man1/bogoupgrade.1*
%{_mandir}/man1/bf_compact.1*
%{_mandir}/man1/bf_copy.1*
%{_mandir}/man1/bf_tar.1*

%{_datadir}/%{name}/contrib-static/*
%endif

%changelog
