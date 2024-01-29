## Process this file with automake to produce makefile.in
CFLAGS = @CFLAGS@ -g -Wall \
	-Wpointer-arith \
	-Wmissing-prototypes -Wmissing-declarations 

SUBDIRS=.

INCLUDES = \
 	-I.					\
	-I..					\
	-DG_DISABLE_DEPRECATED			\
	-DGDK_DISABLE_DEPRECATED		\
	-DGDK_PIXBUF_DISABLE_DEPRECATED		\
	-DGTK_DISABLE_DEPRECATED		\
	-DGNOME_DISABLE_DEPRECATED		\
	-DGNOMELOCALEDIR=\""$(datadir)/locale"\" \
	$(GUI_CFLAGS)

noinst_LIBRARIES = libvicious.a libviciousui.a

noinst_PROGRAMS = test-ve-config

libvicious_a_SOURCES =	\
	ve-misc.c	\
	ve-misc.h	\
	ve-config.c	\
	ve-config.h	\
	ve-signal.c	\
	ve-signal.h	\
	vicious.h

libviciousui_a_SOURCES = \
	$(libvicious_a_SOURCES) \
	glade-helper.c	\
	glade-helper.h	\
	ve-miscui.c	\
	ve-miscui.h	\
	viciousui.h

test_ve_config_SOURCES = \
	test-ve-config.c

test_ve_config_LDADD = \
	$(GUI_LIBS)				\
	$(INTLLIBS)				\
	-L$(top_builddir)/vicious-extensions	\
	-lvicious
