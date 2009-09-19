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
    data/classix.gz \
    data/classix.db

