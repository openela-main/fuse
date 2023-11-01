%global fuse2ver 2.9.7
%global fuse2sver 2
%global fuse3ver 3.3.0

Name:		fuse
Version:	%{fuse2ver}
Release:	16%{?dist}
Summary:	File System in Userspace (FUSE) v2 utilities
License:	GPL+
URL:		http://fuse.sf.net
#fuse2 sources
Source0:	https://github.com/libfuse/libfuse/archive/%{name}-%{fuse2ver}.tar.gz
#fuse3 sources
Source1:	https://github.com/libfuse/libfuse/archive/%{name}-%{fuse3ver}.tar.gz
Source2:	%{name}.conf

Patch1:		fuse-3.0.0-More-parentheses.patch
Patch2:		fuse-0001-More-parentheses.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=970768
Patch3:		fuse-2.9.2-namespace-conflict-fix.patch
Patch4:		fuse-3.2.1-no-dev.patch
Patch5:		fusermount-don-t-feed-escaped-commas-into-mount-opti.patch
Patch6:		buffer_size.patch
Patch7:		fuse-3.10.4-fix-test-failure.patch
Patch8:		0001-Synchronize-fuse_kernel.h.patch
Patch9:		0002-fuse_lowlevel-Add-max_pages-support-384.patch
Patch10:	0003-Allow-caching-symlinks-in-kernel-page-cache.-551.patch
Patch11:	0004-Add-support-for-in-kernel-readdir-caching.patch

Requires:	which
Conflicts:	filesystem < 3
BuildRequires:	libselinux-devel
BuildRequires:	autoconf, automake, libtool, gettext-devel
BuildRequires:	meson, ninja-build, systemd-udev
Requires:	fuse-common = %{fuse3ver}

%description
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE v2 userspace tools to
mount a FUSE filesystem.

%package -n fuse3
Version:	%{fuse3ver}
Summary:	File System in Userspace (FUSE) v3 utilitie
Requires:	fuse-common = %{fuse3ver}
Requires:	fuse3-libs = %{fuse3ver}-%{release}

%description -n fuse3
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE v3 userspace tools to
mount a FUSE filesystem.

%package libs
Version:	%{fuse2ver}
Summary:	File System in Userspace (FUSE) v2 libraries
Group:		System Environment/Libraries
License:	LGPLv2+
Conflicts:	filesystem < 3

%description libs
Devel With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE v2 libraries.

%package -n fuse3-libs
Version:	%{fuse3ver}
Summary:	File System in Userspace (FUSE) v3 libraries
Group:		System Environment/Libraries
License:	LGPLv2+
Conflicts:	filesystem < 3

%description -n fuse3-libs
Devel With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE v3 libraries.

%package devel
Version:	%{fuse2ver}
Summary:	File System in Userspace (FUSE) v2 devel files
Group:		Development/Libraries
Requires:	%{name}-libs = %{fuse2ver}-%{release}
Requires:	pkgconfig
License:	LGPLv2+
Conflicts:	filesystem < 3

%description devel
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains development files (headers,
pgk-config) to develop FUSE v2 based applications/filesystems.

%package -n fuse3-devel
Version:	%{fuse3ver}
Summary:	File System in Userspace (FUSE) v3 devel files
Group:		Development/Libraries
Requires:	%{name}3-libs = %{fuse3ver}-%{release}
Requires:	pkgconfig
License:	LGPLv2+
Conflicts:	filesystem < 3

%description -n fuse3-devel
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains development files (headers,
pgk-config) to develop FUSE v3 based applications/filesystems.

%package common
Version:	%{fuse3ver}
Summary:	Common files for File System in Userspace (FUSE) v2 and v3
License:	GPL+

%description common
Common files for FUSE v2 and FUSE v3.

%prep
%setup -q -T -c -n fuse2and3 -a0 -a1 

# fuse 3
pushd lib%{name}-%{name}-%{fuse3ver}
%patch1 -p1 -b .add_parentheses
%patch4 -p1 -b .nodev
%patch7 -p1 -b .test_fail
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1

popd

# fuse 2
pushd lib%{name}-%{name}-%{fuse2ver}
./makeconf.sh
#disable device creation during build/install
sed -i 's|mknod|echo Disabled: mknod |g' util/Makefile.in
%patch2 -p1 -b .add_parentheses
%patch3 -p1 -b .conflictfix
%patch5 -p1 -b .escaped_commas
%patch6 -p1 -b .buffer_size
popd

%build
# fuse 3
pushd lib%{name}-%{name}-%{fuse3ver}
%meson
%meson_build
%if 0
# Can't pass --disable-static here, or else the utils don't build
export MOUNT_FUSE_PATH="%{_sbindir}"
CFLAGS="%{optflags} -D_GNU_SOURCE" %configure
make %{?_smp_mflags} V=1
%endif
popd

# fuse 2
pushd lib%{name}-%{name}-%{fuse2ver}
# Can't pass --disable-static here, or else the utils don't build
export MOUNT_FUSE_PATH="%{_sbindir}"
CFLAGS="%{optflags} -D_GNU_SOURCE" %configure
make %{?_smp_mflags}
popd

%install
# fuse 3
pushd lib%{name}-%{name}-%{fuse3ver}
export MESON_INSTALL_DESTDIR_PREFIX=%{buildroot}/usr %meson_install
popd
find %{buildroot} .
find %{buildroot} -type f -name "*.la" -exec rm -f {} ';'
# change from 4755 to 0755 to allow stripping -- fixed later in files
chmod 0755 %{buildroot}/%{_bindir}/fusermount3

# fuse 2
pushd lib%{name}-%{name}-%{fuse2ver}
install -m 0755 lib/.libs/libfuse.so.%{fuse2ver} %{buildroot}/%{_libdir}
install -m 0755 lib/.libs/libulockmgr.so.1.0.1 %{buildroot}/%{_libdir}
install -p fuse.pc %{buildroot}/%{_libdir}/pkgconfig/
install -m 0755 util/fusermount %{buildroot}/%{_bindir}
install -m 0755 util/mount.fuse %{buildroot}/%{_sbindir}
install -m 0755 util/ulockmgr_server %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_includedir}/fuse
install -p include/old/fuse.h %{buildroot}/%{_includedir}/
install -p include/ulockmgr.h %{buildroot}/%{_includedir}/
for i in cuse_lowlevel.h fuse_common_compat.h fuse_common.h fuse_compat.h fuse.h fuse_lowlevel_compat.h fuse_lowlevel.h fuse_opt.h; do
	install -p include/$i %{buildroot}/%{_includedir}/fuse/
done
popd
pushd %{buildroot}/%{_libdir}
ln -s libfuse.so.%{fuse2ver} libfuse.so.%{fuse2sver}
ln -s libfuse.so.%{fuse2ver} libfuse.so
ln -s libulockmgr.so.1.0.1 libulockmgr.so.1
ln -s libulockmgr.so.1.0.1 libulockmgr.so
popd
pushd %{buildroot}/%{_mandir}/man8
ln -s mount.fuse3.8 mount.fuse.8
popd

# Get rid of static libs
rm -f %{buildroot}/%{_libdir}/*.a
# No need to create init-script
rm -f %{buildroot}%{_sysconfdir}/init.d/fuse3

# Install config-file
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}

# Delete pointless udev rules, which do not belong in /etc (brc#748204)
rm -f %{buildroot}/usr/lib/udev/rules.d/99-fuse3.rules

%post libs -p /sbin/ldconfig

%post -n fuse3-libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%postun -n fuse3-libs -p /sbin/ldconfig

%files
%license libfuse-fuse-%{fuse2ver}/COPYING
%doc libfuse-fuse-%{fuse2ver}/AUTHORS libfuse-fuse-%{fuse2ver}/ChangeLog libfuse-fuse-%{fuse2ver}/NEWS libfuse-fuse-%{fuse2ver}/README.md libfuse-fuse-%{fuse2ver}/README.NFS
%{_sbindir}/mount.fuse
%attr(4755,root,root) %{_bindir}/fusermount
%{_bindir}/ulockmgr_server

%files -n fuse3
%license libfuse-fuse-%{fuse3ver}/GPL2.txt libfuse-fuse-%{fuse3ver}/LICENSE

%doc libfuse-fuse-%{fuse3ver}/AUTHORS libfuse-fuse-%{fuse3ver}/ChangeLog.rst libfuse-fuse-%{fuse3ver}/README.md
%{_sbindir}/mount.fuse3
%attr(4755,root,root) %{_bindir}/fusermount3

%files common
%config(noreplace) %{_sysconfdir}/%{name}.conf
%{_mandir}/man1/*
%{_mandir}/man8/*

%files libs
%license libfuse-fuse-%{fuse2ver}/COPYING.LIB
%{_libdir}/libfuse.so.*
%{_libdir}/libulockmgr.so.*

%files -n fuse3-libs
%license libfuse-fuse-%{fuse3ver}/LGPL2.txt
%{_libdir}/libfuse3.so.*

%files devel
%{_libdir}/libfuse.so
%{_libdir}/libulockmgr.so
%{_libdir}/pkgconfig/fuse.pc
%{_includedir}/fuse.h
%{_includedir}/ulockmgr.h
%{_includedir}/fuse

%files -n fuse3-devel
%{_libdir}/libfuse3.so
%{_libdir}/pkgconfig/fuse3.pc
%{_includedir}/fuse3/

%changelog
* Mon May 30 2022 Pavel Reichl <preichl@redhat.com> - 2.9.7-16
- Back-port max_pages support,
- caching symlinks in kernel page cache,
- and in-kernel readdir caching
- Fixed rhbz#2080000

* Wed Feb 23 2022 Pavel Reichl <preichl@redhat.com> - 2.9.7-15
- Fix missing dependency of fuse3 on fuse3-libs
- Make symlink for mount.fuse to mount.fuse3

* Mon Feb 07 2022 Pavel Reichl <preichl@redhat.com> - 2.9.7-14
- Fix failing test for fuse-3

* Mon Jan 31 2022 Pavel Reichl <preichl@redhat.com> - 2.9.7-13
- update to 3.3.0
- patch #5 is part of fuse-3 upstream now

* Thu Nov 08 2018 Miklos Szeredi <mszeredi@redhat.com> - 2.9.7-12
- Fixed CVE-2018-10906 (rhbz#1607855)
- Fix regression from RHEL7 (rhbz#1648280)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.7-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Nov 16 2017 Tom Callaway <spot@fedoraproject.org> 2.9.7-10
- update fuse3 to 3.2.1

* Mon Aug  7 2017 Tom Callaway <spot@fedoraproject.org> 2.9.7-9
- update fuse3 to 3.1.1

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.7-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Fri Jul 28 2017 Tom Callaway <spot@fedoraproject.org> - 2.9.7-7
- use -D_FILE_OFFSET_BITS=64 to force off_t to be 64bit on 32bit arches

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.7-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 17 2017 Tom Callaway <spot@fedoraproject.org> - 3.1.0-5
- update to 3.1.0

* Thu Jun  1 2017 Tom Callaway <spot@fedoraproject.org> - 3.0.2-4
- update to 3.0.2

* Sun Mar 26 2017 Tom Callaway <spot@fedoraproject.org> - 3.0.0-3
- update release to 3 to make clean upgrade

* Tue Mar 21 2017 Tom Callaway <spot@fedoraproject.org> - 3.0.0-1
- update to 3.0.0
- split out fuse3 packages

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Jul  6 2016 Tom Callaway <spot@fedoraproject.org> - 2.9.7-1
- update to 2.9.7

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Oct 08 2015 Adam Williamson <awilliam@redhat.com> - 2.9.4-3
- backport patch allowing setting SELinux context on FUSE mounts

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.9.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri May 22 2015 Tom Callaway <spot@fedoraproject.org> 2.9.4-1
- update to 2.9.4
- fixes CVE-2015-3202

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.9.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.9.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.9.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Jul  6 2013 Tom Callaway <spot@fedoraproject.org> - 2.9.3-1
- update to 2.9.3

* Wed Jun 26 2013 Tom Callaway <spot@fedoraproject.org> - 2.9.2-4
- add fix for namespace conflict in fuse_kernel.h

* Sat May 18 2013 Peter Lemenkov <lemenkov@gmail.com> - 2.9.2-3
- Removed pre-F12 stuff
- Dropped ancient dependency on initscripts and chkconfig

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Dec 06 2012 Adam Jackson <ajax@redhat.com>
- Remove ancient Requires: kernel >= 2.6.14, FC6 was 2.6.18.

* Tue Oct 23 2012 Tom Callaway <spot@fedoraproject.org> - 2.9.2-1
- update to 2.9.2

* Tue Aug 28 2012 Tom Callaway <spot@fedoraproject.org> - 2.9.1-1
- update to 2.9.1

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Apr 16 2012 Peter Lemenkov <lemenkov@gmail.com> - 2.8.7-1
- Ver. 2.8.7

* Sun Apr 15 2012 Kay Sievers <kay@redhat.com> - 2.8.6-4
- remove needless udev rule

* Wed Jan 25 2012 Harald Hoyer <harald@redhat.com> 2.8.6-3
- install everything in /usr
  https://fedoraproject.org/wiki/Features/UsrMove

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Sep 22 2011 Peter Lemenkov <lemenkov@gmail.com> - 2.8.6-1
- Ver. 2.8.6
- Dropped patch 3 - fixed upstream

* Thu Mar 03 2011 Peter Lemenkov <lemenkov@gmail.com> - 2.8.5-5
- Use noreplace for /etc/fuse.conf

* Tue Feb 15 2011 Peter Lemenkov <lemenkov@gmail.com> - 2.8.5-4
- Provide /etc/fuse.conf (see rhbz #292811)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Oct 27 2010 Peter Lemenkov <lemenkov@gmail.com> 2.8.5-2
- Fixed rhbz #622255

* Tue Oct 26 2010 Peter Lemenkov <lemenkov@gmail.com> 2.8.5-1
- Ver. 2.8.5

* Tue Jun  8 2010 Peter Lemenkov <lemenkov@gmail.com> 2.8.4-1
- Ver. 2.8.4
- CVE-2009-3297 patch dropped (merged upstream)

* Tue Jan 26 2010 Peter Lemenkov <lemenkov@gmail.com> 2.8.1-4
- Fixed CVE-2009-3297 (rhbz #558833)

* Thu Nov 19 2009 Peter Lemenkov <lemenkov@gmail.com> 2.8.1-3
- Fixed udev rules (bz# 538606)

* Thu Nov 19 2009 Peter Lemenkov <lemenkov@gmail.com> 2.8.1-2
- Removed support for MAKEDEV (bz# 511220)

* Thu Sep 17 2009 Peter Lemenkov <lemenkov@gmail.com> 2.8.1-1
- Ver. 2.8.1

* Wed Aug 19 2009 Peter Lemenkov <lemenkov@gmail.com> 2.8.0-1
- Ver. 2.8.0

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jan 28 2009 Peter Lemenkov <lemenkov@gmail.com> 2.7.4-2
- Fixed BZ#479581

* Sat Aug 23 2008 Peter Lemenkov <lemenkov@gmail.com> 2.7.4-1
- Ver. 2.7.4

* Sat Jul 12 2008 Peter Lemenkov <lemenkov@gmail.com> 2.7.3-3
- Fixed initscripts (BZ#441284)

* Thu Feb 28 2008 Peter Lemenkov <lemenkov@gmail.com> 2.7.3-2
- Fixed BZ#434881

* Wed Feb 20 2008 Peter Lemenkov <lemenkov@gmail.com> 2.7.3-1
- Ver. 2.7.3
- Removed usergroup fuse
- Added chkconfig support (BZ#228088)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.7.2-2
- Autorebuild for GCC 4.3

* Mon Jan 21 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.2-1
- bump to 2.7.2
- fix license tag

* Sun Nov  4 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-9
- fix initscript to work with chkconfig

* Mon Oct  1 2007 Peter Lemenkov <lemenkov@gmail.com> 2.7.0-8
- Added Require: which (BZ#312511)

* Fri Sep 21 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-7
- revert udev rules change

* Thu Sep 20 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-6
- change udev rules so that /dev/fuse is chmod 666 (bz 298651)

* Wed Aug 29 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-5
- fix open issue (bz 265321)

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 2.7.0-4
- Rebuild for selinux ppc32 issue.

* Sun Jul 22 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-3
- put pkgconfig file in correct place
- enable compat symlinks for files in /bin

* Sat Jul 21 2007 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.0-2
- redefine exec_prefix to /
- redefine bindir to /bin
- redefine libdir to %%{_lib}
- don't pass --disable-static to configure
- manually rm generated static libs

* Wed Jul 18 2007 Peter Lemenkov <lemenkov@gmail.com> 2.7.0-1
- Version 2.7.0
- Redefined exec_prefix due to demands from NTFS-3G

* Wed Jun  6 2007 Peter Lemenkov <lemenkov@gmail.com> 2.6.5-2
- Add BR libselinux-devel (bug #235145)
- Config files properly marked as config (bug #211122)

* Sat May 12 2007 Peter Lemenkov <lemenkov@gmail.com> 2.6.5-1
- Version 2.6.5

* Thu Feb 22 2007 Peter Lemenkov <lemenkov@gmail.com> 2.6.3-2
- Fixed bug #229642

* Wed Feb  7 2007 Peter Lemenkov <lemenkov@gmail.com> 2.6.3-1
* Ver. 2.6.3

* Tue Dec 26 2006 Peter Lemenkov <lemenkov@gmail.com> 2.6.1-1
- Ver. 2.6.1

* Sat Nov 25 2006 Peter Lemenkov <lemenkov@gmail.com> 2.6.0-2
- fixed nasty typo (see bug #217075)

* Fri Nov  3 2006 Peter Lemenkov <lemenkov@gmail.com> 2.6.0-1
- Ver. 2.6.0

* Sun Oct 29 2006 Peter Lemenkov <lemenkov@gmail.com> 2.5.3-5
- Fixed udev-rule again

* Sat Oct  7 2006 Peter Lemenkov <lemenkov@gmail.com> 2.5.3-4
- Fixed udev-rule

* Tue Sep 12 2006 Peter Lemenkov <lemenkov@gmail.com> 2.5.3-3%{?dist}
- Rebuild for FC6

* Wed May 03 2006 Peter Lemenkov <lemenkov@newmail.ru> 2.5.3-1%{?dist}
- Update to 2.5.3

* Thu Mar 30 2006 Peter Lemenkov <lemenkov@newmail.ru> 2.5.2-4%{?dist}
- rebuild

* Mon Feb 13 2006 Peter Lemenkov <lemenkov@newmail.ru> - 2.5.2-3
- Proper udev rule

* Mon Feb 13 2006 Peter Lemenkov <lemenkov@newmail.ru> - 2.5.2-2
- Added missing requires

* Tue Feb 07 2006 Peter Lemenkov <lemenkov@newmail.ru> - 2.5.2-1
- Update to 2.5.2
- Dropped fuse-mount.fuse.patch

* Wed Nov 23 2005 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 2.4.2-1
- Use dist

* Wed Nov 23 2005 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 2.4.2-1
- Update to 2.4.2 (solves CVE-2005-3531)
- Update README.fedora

* Sat Nov 12 2005 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 2.4.1-3
- Add README.fedora
- Add hint to README.fedora and that you have to be member of the group "fuse"
  in the description
- Use groupadd instead of fedora-groupadd

* Fri Nov 04 2005 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 2.4.1-2
- Rename packages a bit
- use makedev.d/40-fuse.nodes
- fix /sbin/mount.fuse
- Use a fuse group to restict access to fuse-filesystems

* Fri Oct 28 2005 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 2.4.1-1
- Initial RPM release.
