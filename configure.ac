# -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_INIT(classix, 0.1, http://code.google.com/p/classix/issues/list,
    ,http://code.google.com/p/classix/)
AC_CONFIG_SRCDIR(classix.in)
AM_INIT_AUTOMAKE
AM_MAINTAINER_MODE

AM_PATH_PYTHON(2.5)
# TODO: Check dependencies

GETTEXT_PACKAGE=classix
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.40.0])

AC_CONFIG_FILES([
        Makefile
        po/Makefile.in])
AC_OUTPUT
