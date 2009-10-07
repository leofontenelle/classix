## Process this file with automake to produce Makefile.in
## AUTOMAKE_OPTIONS = subdir-objects
SUBDIRS = data po src


bin_SCRIPTS = classix
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = classix.in
     
classix: classix.in Makefile
	sed -e s![@]PYTHON[@]!@PYTHON@! < $< > $@


DISTCLEANFILES = \
	intltool-extract \
	intltool-merge   \
	intltool-update  \
	po/.intltool-merge-cache
	
EXTRA_DIST += \
	intltool-extract.in \
	intltool-merge.in   \
	intltool-update.in

## TODO: include debian/* files if they are found.
