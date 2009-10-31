do_subst = sed \
	-e s![@]PYTHON[@]![@]PYTHON[@]! 	\
	-e s![@]prefix[@]!$(prefix)!g		\
	-e s![@]datadir[@]!$(datadir)!g		\
	-e s![@]pkgdatadir[@]!$(pkgdatadir)!g	\
	-e s![@]libexecdir[@]!$(libexecdir)!g	\
	-e s![@]libdir[@]!$(libdir)!g		\
	-e s![@]PACKAGE[@]!$(PACKAGE)!g		\
	-e s![@]VERSION[@]!$(VERSION)!g		
	
pkgpython_PYTHON = __init__.py main.py config.py

CLEANFILES = config.py
EXTRA_DIST = config.py.in

config.py: config.py.in Makefile
	$(do_subst) < $< > $@


