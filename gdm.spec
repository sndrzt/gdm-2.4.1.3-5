%define localstatedir /var/lib
%define sysconfdir    /etc

Summary:        The GNOME Display Manager.
Name:           gdm
Version:        2.4.1.3
Release:        1
Epoch:          1
License:        LGPL/GPL
Group:          User Interface/X
Source:         ftp://ftp.5z.com/pub/unix/gdm-%{version}.tar.gz
BuildRoot:      %{_tmppath}/gdm-%{version}-root
Prereq:         /usr/sbin/useradd
Requires:       pam >= 0.68
Requires:       gnome-libs >= 1.0.17
BuildRequires:  usermode, libglade-devel
BuildRequires:  gnome-libs-devel >= 1.0.17
BuildRequires:  gdk-pixbuf-devel >= 0.7.0

%description
Gdm (the GNOME Display Manager) is a highly configurable
reimplementation of xdm, the X Display Manager. Gdm allows you to log
into your system with the X Window System running and supports running
several different X sessions on your local machine at the same time.

%prep
%setup -q

%build
CFLAGS="-g $RPM_OPT_FLAGS" ./configure --localstatedir=%{localstatedir} \
    --prefix=%{_prefix} --sysconfdir=%{sysconfdir}/X11 \
    --bindir=%{_bindir} --datadir=%{_datadir} --sbindir=%{_sbindir} \
    --enable-console-helper --with-pam-prefix=%{sysconfdir}

make

%install
rm -rf $RPM_BUILD_ROOT

/usr/sbin/useradd -r gdm > /dev/null 2>&1 || /bin/true

make sysconfdir=$RPM_BUILD_ROOT%{sysconfdir}/X11 \
    prefix=$RPM_BUILD_ROOT%{_prefix} \
    bindir=$RPM_BUILD_ROOT%{_bindir} \
    datadir=$RPM_BUILD_ROOT%{_datadir} \
    localstatedir=$RPM_BUILD_ROOT%{localstatedir} \
    sbindir=$RPM_BUILD_ROOT%{_sbindir} \
    PAM_PREFIX=$RPM_BUILD_ROOT%{sysconfdir} \
    install


# install RH specific session files
rm -f $RPM_BUILD_ROOT%{sysconfdir}/X11/gdm/Sessions/*

install -m 755 config/Default.redhat $RPM_BUILD_ROOT%{sysconfdir}/X11/gdm/Sessions/Default
install -m 755 config/Gnome $RPM_BUILD_ROOT%{sysconfdir}/X11/gdm/Sessions/Gnome
ln -sf Default $RPM_BUILD_ROOT%{sysconfdir}/X11/gdm/Sessions/default

# change default Init script to be Red Hat default
# Note that this just sets up background and we already do that ourselves
#ln -sf ../../xdm/Xsetup_0 $RPM_BUILD_ROOT%{sysconfdir}/X11/gdm/Init/Default

# done right nowdays
# move pam.d stuff to right place
# mv $RPM_BUILD_ROOT%{sysconfdir}/X11/pam.d $RPM_BUILD_ROOT%{sysconfdir}
# move security stuff to right place
# mv $RPM_BUILD_ROOT%{sysconfdir}/X11/security $RPM_BUILD_ROOT%{sysconfdir}
%find_lang %{name}

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

%pre
/usr/sbin/useradd -u 42 -r gdm > /dev/null 2>&1
# ignore errors, as we can't disambiguate between gdm already existed
# and couldn't create account with the current adduser.
exit 0

%post
# Attempt to restart GDM softly by use of the fifo.  Wont work on older
# then 2.2.3.1 versions but should work nicely on later upgrades.
# FIXME: this is just way too complex
FIFOFILE=`grep '^ServAuthDir=' %{sysconfdir}/X11/gdm/gdm.conf | sed -e 's/^ServAuthDir=//'`
if test x$FIFOFILE = x ; then
	FIFOFILE=%{localstatedir}/gdm/.gdmfifo
else
	FIFOFILE="$FIFOFILE"/.gdmfifo
fi
PIDFILE=`grep '^PidFile=' %{sysconfdir}/X11/gdm/gdm.conf | sed -e 's/^PidFile=//'`
if test x$PIDFILE = x ; then
	PIDFILE=/var/run/gdm.pid
fi
if test -w $FIFOFILE ; then
	if test -f $PIDFILE ; then
		if kill -0 `cat $PIDFILE` ; then
			(echo;echo SOFT_RESTART) >> $FIFOFILE
		fi
	fi
fi
# ignore error in the above
exit 0

%files -f %name.lang
%defattr(-, root, root)

%doc AUTHORS COPYING ChangeLog NEWS README
%{_bindir}/*
%{_sbindir}/*
%config %{sysconfdir}/pam.d/*
%config %{sysconfdir}/X11/*
%config %{sysconfdir}/security/console.apps/*
%{_datadir}/pixmaps/*
%{_datadir}/gdm
%{_datadir}/gnome/apps/*/*
%{_datadir}/gnome/help/*
%{_datadir}/omf/gdm
# %config %{sysconfdir}/security/console.apps/gdmsetup
# %config %{sysconfdir}/X11/gdm/gnomerc
# %config %{sysconfdir}/X11/gdm/gdm.conf
# %config %{sysconfdir}/X11/gdm/locale.alias
# %config %{sysconfdir}/X11/gdm/Sessions/*
# %config %{sysconfdir}/X11/gdm/Init/*
# %config %{sysconfdir}/X11/gdm/PreSession/*
# %config %{sysconfdir}/X11/gdm/PostSession/*
# %{_datadir}/gdm/gdmsetup.glade
# %{_datadir}/gdm/gdmchooser.glade
# %{_datadir}/gnome/apps/System/gdmsetup.desktop
# %{_datadir}/gnome/apps/Settings/gdmphotosetup.desktop
# %{_datadir}/locale/*/*/*
# %{_datadir}/pixmaps/*
# %{_datadir}/gnome/help/gdm/*
# %{_datadir}/gnome/help/gdmsetup/*
%attr(750, gdm, gdm) %dir %{localstatedir}/gdm


%changelog
* Tue Nov  6 2001 Gregory Leblanc <gleblanc@linuxweasel.com>
- removed some unnecessary %defines
- fixed find_lang stuff
- added some BuildRequires lines

* Sun Jul 01 2001 George Lebl <jirka@5z.com>
- Fixed file listing

* Sun May 24 2001 George Lebl <jirka@5z.com>
- Hmmm, simplified the file listing, dunno why normally people list
  things file by file/dir by dir, but the old file list was out of date

* Sun May 06 2001 George Lebl <jirka@5z.com>
- Kill the Failsafe script. GDM will now do failsafe itself, in an actual
  failsafe way (meaning it will work with greater degree of hosage)

* Wed Mar 07 2001 George Lebl <jirka@5z.com>
- Fixups, move the security dir as well and build with console helper and
  hardwire the sysconfdir to /etc as that seems broke on my 6.2 box otherwise

* Wed Mar 07 2001 Gregory Leblanc <gleblanc@cu-portland.edu>
- finalize patches that have been pending.  Merge changes forward, and
  commit to CVS.

* Mon Mar 05 2001 Lee Mallabone <lee0@callnetuk.com>
- Change glade file paths and add gdmchooser glade file.

* Wed Feb 28 2001 Lee Mallabone <lee0@callnetuk.com>
- Add necessary paths/flags to use console-helper for gdmconfig.

* Thu Feb 22 2001 Gregory Leblanc <gleblanc@cu-portland.edu>
- %define localstatedir /var/lib and related changes

* Tue Feb 20 2001 Gregory Leblanc <gleblanc@cu-portland.edu>
- macro cleanups

* Fri Feb 03 2001 George Lebl <jirka@5z.com>
- Add gdmconfig files

* Fri Feb 02 2001 George Lebl <jirka@5z.com>
- Remove all the patches and do the voodoo that I don't do so well
  to make this thingie work with 2.0.97.1

* Fri Feb 04 2000 Havoc Pennington <hp@redhat.com>
- Modify Default.session and Failsafe.session not to add -login option to bash
- exec the session scripts with the user's shell with a hyphen prepended
- doesn't seem to actually work yet with tcsh, but it doesn't seem to 
  break anything. needs a look to see why it doesn't work

* Fri Feb 04 2000 Havoc Pennington <hp@redhat.com>
- Link PreSession/Default to xdm/GiveConsole
- Link PostSession/Default to xdm/TakeConsole

* Fri Feb 04 2000 Havoc Pennington <hp@redhat.com>
- Fix the fix to the fix (8877)
- remove docs/gdm-manual.txt which doesn't seem to exist from %doc

* Fri Feb 04 2000 Havoc Pennington <hp@redhat.com>
- Enhance 8877 fix by not deleting the "Please login" 
  message

* Fri Feb 04 2000 Havoc Pennington <hp@redhat.com>
- Try to fix bug 8877 by clearing the message below 
  the entry box when the prompt changes. may turn 
  out to be a bad idea.

* Mon Jan 17 2000 Elliot Lee <sopwith@redhat.com>
- Fix bug #7666: exec Xsession instead of just running it

* Mon Oct 25 1999 Jakub Jelinek <jakub@redhat.com>
- Work around so that russian works (uses koi8-r instead
  of the default iso8859-5)

* Tue Oct 12 1999 Owen Taylor <otaylor@redhat.com>
- Try again

* Tue Oct 12 1999 Owen Taylor <otaylor@redhat.com>
- More fixes for i18n

* Tue Oct 12 1999 Owen Taylor <otaylor@redhat.com>
- Fixes for i18n

* Fri Sep 26 1999 Elliot Lee <sopwith@redhat.com>
- Fixed pipewrite bug (found by mkj & ewt).

* Fri Sep 17 1999 Michael Fulbright <drmike@redhat.com>
- added requires for pam >= 0.68

* Fri Sep 10 1999 Elliot Lee <sopwith@redhat.com>
- I just update this package every five minutes, so any recent changes are my fault.

* Thu Sep 02 1999 Michael K. Johnson <johnsonm@redhat.com>
- built gdm-2.0beta2

* Mon Aug 30 1999 Michael K. Johnson <johnsonm@redhat.com>
- built gdm-2.0beta1

* Tue Aug 17 1999 Michael Fulbright <drmike@redhat.com>
- included rmeier@liberate.com patch for tcp socket X connections

* Mon Apr 19 1999 Michael Fulbright <drmike@redhat.com>
- fix to handling ancient gdm config files with non-standard language specs
- dont close display connection for xdmcp connections, else we die if remote
  end dies. 

* Fri Apr 16 1999 Michael Fulbright <drmike@redhat.com>
- fix language handling to set GDM_LANG variable so gnome-session 
  can pick it up

* Wed Apr 14 1999 Michael Fulbright <drmike@redhat.com>
- fix so certain dialog boxes dont overwrite background images

* Wed Apr 14 1999 Michael K. Johnson <johnsonm@redhat.com>
- do not specify -r 42 to useradd -- it doesn't know how to fall back
  if id 42 is already taken

* Fri Apr 9 1999 Michael Fulbright <drmike@redhat.com>
- removed suspend feature

* Mon Apr 5 1999 Jonathan Blandford <jrb@redhat.com>
- added patch from otaylor to not call gtk funcs from a signal.
- added patch to tab when username not added.
- added patch to center About box (and bring up only one) and ignore "~"
  and ".rpm" files.

* Fri Mar 26 1999 Michael Fulbright <drmike@redhat.com>
- fixed handling of default session, merged all gdmgreeter patches into one

* Tue Mar 23 1999 Michael Fulbright <drmike@redhat.com>
- remove GNOME/KDE/AnotherLevel session scripts, these have been moved to
  the appropriate packages instead.
- added patch to make option menus always active (security problem otherwise)
- added jrb's patch to disable stars in passwd entry field

* Fri Mar 19 1999 Michael Fulbright <drmike@redhat.com>
- made sure /usr/bin isnt in default path twice
- strip binaries

* Wed Mar 17 1999 Michael Fulbright <drmike@redhat.com>
- fixed to use proper system path when root logs in

* Tue Mar 16 1999 Michael Fulbright <drmike@redhat.com>
- linked Init/Default to Red Hat default init script for xdm
- removed logo from login dialog box

* Mon Mar 15 1999 Michael Johnson <johnsonm@redhat.com>
- pam_console integration

* Tue Mar 09 1999 Michael Fulbright <drmike@redhat.com>
- added session files for GNOME/KDE/AnotherLevel/Default/Failsafe
- patched gdmgreeter to not complete usernames
- patched gdmgreeter to not safe selected session permanently
- patched gdmgreeter to center dialog boxes

* Mon Mar 08 1999 Michael Fulbright <drmike@redhat.com>
- removed comments from gdm.conf file, these are not parsed correctly

* Sun Mar 07 1999 Michael Fulbright <drmike@redhat.com>
- updated source line for accuracy

* Fri Feb 26 1999 Owen Taylor <otaylor@redhat.com>
- Updated patches for 1.0.0
- Fixed some problems in 1.0.0 with installation directories
- moved /usr/var/gdm /var/gdm

* Thu Feb 25 1999 Michael Fulbright <drmike@redhat.com>
- moved files from /usr/etc to /etc

* Tue Feb 16 1999 Michael Johnson <johnsonm@redhat.com>
- removed commented-out #1 definition -- put back after testing gnome-libs
  comment patch

* Sat Feb 06 1999 Michael Johnson <johnsonm@redhat.com>
- initial packaging
