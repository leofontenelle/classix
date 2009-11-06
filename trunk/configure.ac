# -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_INIT(Classix, 0.3, http://code.google.com/p/classix/issues, classix,
	http://code.google.com/p/classix/)
AC_COPYRIGHT([Copyright (C) 2009 the Classix authors.
This file is distributed under the same license as the AC_PACKAGE_NAME package.])
AC_CONFIG_SRCDIR(classix.in)
AM_INIT_AUTOMAKE
AM_MAINTAINER_MODE
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES])

AM_PATH_PYTHON(2.5)
# TODO: Check dependencies

GETTEXT_PACKAGE=classix
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.40.0])

AC_ARG_ENABLE(
	[maemo],
	[AS_HELP_STRING([--enable-maemo],[Maemo specificities (default: no.)])]
	[use_maemo=yes])
AM_CONDITIONAL([MAEMO], [test "x$use_maemo" = "xyes"])

AC_CONFIG_FILES([
	Makefile
	bin/Makefile
	classix/Makefile
	data/Makefile
	po/Makefile.in])
AC_OUTPUT
