SUBDIRS = po

bin_SCRIPTS = classix
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = classix.in
     
classix: classix.in
	sed -e s!\@PYTHON\@!@PYTHON@! < $< > $@
classix: Makefile


pkgpython_PYTHON = \
	src/__init__.py \
	src/main.py \
	src/config.py

CLEANFILES += src/config.py
EXTRA_DIST += src/config.py.in

src/config.py: src/config.py.in
	sed						\
		-e s!\@prefix\@!$(prefix)!		\
		-e s!\@datadir\@!$(datadir)!		\
		-e s!\@pkgdatadir\@!$(pkgdatadir)!	\
		-e s!\@libexecdir\@!$(libexecdir)!	\
		-e s!\@libdir\@!$(libdir)!		\
		-e s!\@PACKAGE\@!$(PACKAGE)!		\
		-e s!\@VERSION\@!$(VERSION)!		\
		< $< > $@
src/config.py: Makefile


dist_pkgdata_DATA = \
	data/classix.ui \
	data/classix.db


desktopdir = $(datadir)/applications
desktop_in_files = data/classix.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@


CLEANFILES += $(desktop_DATA)
EXTRA_DIST += $(desktop_in_files)


DISTCLEANFILES = \
	intltool-extract \
	intltool-merge   \
	intltool-update
	
EXTRA_DIST += \
	intltool-extract.in \
	intltool-merge.in   \
	intltool-update.in
