## Process this file with automake to produce makefile.in
CFLAGS = @CFLAGS@ -g -Wall 	\
	-Wpointer-arith  	\
	-Wmissing-prototypes -Wmissing-declarations 

DEFS = @DEFS@ -DGDM_CONFIG_FILE=\"@sysconfdir@/gdm/gdm.conf\" \
	-DGDM_FACTORY_CONFIG_FILE=\"@sysconfdir@/gdm/factory-gdm.conf\" \
	-DGDM_GLADE_DIR=\"@datadir@/gdm\"

INCLUDES = \
	-I.						\
	-I..						\
	-I$(top_srcdir)/daemon				\
	-I$(top_srcdir)/vicious-extensions		\
	-DGNOMELOCALEDIR=\""$(datadir)/locale"\" 	\
	$(UTILS_CFLAGS)

sbin_PROGRAMS = \
	@GDMASKPASS@	\
	@GDMOPEN@

bin_PROGRAMS = \
	gdmmktemp

EXTRA_PROGRAMS = gdmaskpass gdmopen

gdmaskpass_SOURCES = \
	gdmaskpass.c

gdmopen_SOURCES = \
	gdmopen.c

gdmmktemp_SOURCES = \
	gdmmktemp.c

gdmaskpass_LDADD = \
	$(INTLLIBS)		\
	-lpam			\
	-lpam_misc

gdmopen_LDADD = \
	$(INTLLIBS)

gdmmktemp_LDADD = \
	$(INTLLIBS)
