dist_pkgdata_DATA = classix.ui classix.db


if MAEMO
desktopdir = $(datadir)/applications/hildon
else
desktopdir = $(datadir)/applications
endif
desktop_in_files = classix.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

CLEANFILES = $(desktop_DATA)
EXTRA_DIST = $(desktop_in_files)



