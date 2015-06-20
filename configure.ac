# -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

GNOME_COMMON_INIT

AC_INIT(Classix, 0.4, https://github.com/leofontenelle/classix/issues,
 classix,	http://github.com/leofontenelle/classix/)
AC_COPYRIGHT([Copyright (C) 2009-2012 Leonardo Ferreira Fontenelle <leonardof@gnome.org>.
This file is distributed under the same license as the AC_PACKAGE_NAME package.])
AC_CONFIG_SRCDIR(src/classix.vala)
AM_INIT_AUTOMAKE([foreign])
AM_MAINTAINER_MODE
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES])

AC_PROG_CC
AC_PROG_CC_STDC
AM_PROG_VALAC([0.14])
AC_PROG_INSTALL

pkg_modules="gee-1.0 >= 0.6 gtk+-3.0 gmodule-2.0 gio-2.0"
CLASSIX_PACKAGES="--pkg gtk+-3.0 --pkg gmodule-2.0 --pkg gee-1.0 --pkg gio-2.0"
PKG_CHECK_MODULES(CLASSIX, [$pkg_modules])
AC_SUBST(CLASSIX_CFLAGS)
AC_SUBST(CLASSIX_LIBS)
AC_SUBST(CLASSIX_PACKAGES)

# No gettext or intltool

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
