bin_SCRIPTS = classix
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = classix.in
     
classix: classix.in Makefile
	sed -e s![@]PYTHON[@]!@PYTHON@! < $< > $@
