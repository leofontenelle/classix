## Process this file with automake to produce Makefile.in
## AUTOMAKE_OPTIONS = subdir-objects

bin_PROGRAMS = classix
classix_SOURCES = src/classix.vala

INCLUDES = $(CLASSIX_CFLAGS) \
           -DLOCALEDIR=\""$(localedir)"\" \
           -DPKGDATADIR=\""$(pkgdatadir)"\" \
           -DPKGLIBDIR=\""$(pkglibdir)"\"

VALAFLAGS = @CLASSIX_PACKAGES@

classix_LDADD = $(CLASSIX_LIBS)

dist_pkgdata_DATA = data/CID10N4A.DAT \
                    data/CID10N4A.DIC \
                    data/CID10N4A.INV \
                    data/classix.ui
EXTRA_DIST = data/classix.desktop

desktopdir = $(datadir)/applications
desktop_DATA = data/classix.desktop

dist_doc_DATA = AUTHORS COPYING HACKING INSTALL LEIAME NEWS README
