/* Glade helper routines
 *
 * Author: George Lebl
 * (c) 2000 Eazel, Inc.
 * (c) 2002 George Lebl
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

#include <config.h>

/* For clist */
#undef GTK_DISABLE_DEPRECATED

#include <libgnome/libgnome.h>
#include <libgnomeui/libgnomeui.h>
#include <glade/glade.h>

#include "ve-misc.h"

#include "glade-helper.h"

static void glade_helper_no_interface (const char *filename);
static void glade_helper_bad_interface (const char *filename,
					const char *widget,
					GType type);
static void glade_helper_bad_columns (const char *filename,
				      const char *widget,
				      GType type,
				      int columns);

static GList *ve_glade_directories = NULL;
static gboolean ve_search_gnome_dirs = TRUE;

GladeXML *
glade_helper_load (const char *file, const char *widget,
		   GType expected_type,
		   gboolean dump_on_destroy)
{
	char *f;
	GladeXML *xml;
	GtkWidget *w;

	g_return_val_if_fail (file != NULL, NULL);

	f = glade_helper_find_glade_file (file);

	if (f == NULL) {
		glade_helper_no_interface (file);
		exit (1);
	}

	/* FIXME: eek use of PACKAGE */
	xml = glade_xml_new (f, widget, GETTEXT_PACKAGE);

	g_free (f);

	/* in case we can't load the interface, bail */
	if (xml == NULL) {
		glade_helper_no_interface (file);
		exit (1);
	}

	w = glade_xml_get_widget (xml, widget);
	if (w == NULL ||
	    ! G_TYPE_CHECK_INSTANCE_TYPE (w, expected_type)) {
		glade_helper_bad_interface (xml->filename != NULL ?
					      xml->filename :
					      _("(memory buffer)"),
					    widget,
					    expected_type);
		exit (1);
	}

	if (dump_on_destroy) {
		g_object_set_data_full (G_OBJECT (w),
					"GladeXML",
					xml,
					(GtkDestroyNotify) g_object_unref);
	}

	return xml;
}

GtkWidget *
glade_helper_load_widget (const char *file, const char *widget,
			  GType expected_type)
{
	GladeXML *xml;
	GtkWidget *w;

	/* this is guaranteed to return non-NULL, otherwise we
	 * would have exited */
	xml = glade_helper_load (file, widget, expected_type, FALSE);

	w = glade_xml_get_widget (xml, widget);
	if (w == NULL ||
	    ! G_TYPE_CHECK_INSTANCE_TYPE (w, expected_type)) {
		glade_helper_bad_interface (xml->filename != NULL ?
					      xml->filename :
					      _("(memory buffer"),
					    widget,
					    expected_type);
		exit (1);
	}

	g_object_unref (G_OBJECT (xml));
	
	return w;
}

GtkWidget *
glade_helper_get (GladeXML *xml, const char *widget, GType expected_type)
{
	GtkWidget *w;

	w = glade_xml_get_widget (xml, widget);

	if (w == NULL ||
	    ! G_TYPE_CHECK_INSTANCE_TYPE (w, expected_type)) {
		glade_helper_bad_interface (xml->filename != NULL ?
					      xml->filename :
					      _("(memory buffer"),
					    widget,
					    expected_type);
		exit (1);
	}

	return w;
}

GtkWidget *
glade_helper_get_clist (GladeXML *xml, const char *widget,
			GType expected_type, int expected_columns)
{
	GtkWidget *w;

	w = glade_helper_get (xml, widget, expected_type);

	if (GTK_CLIST (w)->columns != expected_columns) {
		glade_helper_bad_columns (xml->filename != NULL ?
					    xml->filename :
					    _("(memory buffer"),
					  widget,
					  expected_type,
					  expected_columns);
		exit (1);
	}

	return w;
}

static void
glade_helper_bad_interface (const char *filename, const char *widget,
			    GType type)
{
	GtkWidget *dlg;
	char *typestring;
	const char *typename;

	if (type != 0)
		typename = g_type_name (type);
	else
		typename = NULL;

	if (typename == NULL)
		typestring = g_strdup_printf (" (%s)", typename);
	else
		typestring = g_strdup ("");
	
	dlg = gtk_message_dialog_new (NULL /* parent */,
				      0 /* flags */,
				      GTK_MESSAGE_ERROR,
				      GTK_BUTTONS_CLOSE,
				      _("An error occured while loading the user "
					"interface\nelement %s%s from file %s.\n"
					"Possibly the glade interface description was "
					"corrupted.\n"
					"%s cannot continue and will exit now.\n"
					"You should check your "
					"installation of %s or reinstall %s."),
				      widget,
				      typestring,
				      filename,
				      PACKAGE,
				      PACKAGE,
				      PACKAGE);

	g_free (typestring);

	g_warning (_("Glade file is on crack! Make sure the correct "
		     "file is installed!\nfile: %s widget: %s"),
		   filename, widget);

	gtk_dialog_run (GTK_DIALOG (dlg));
	gtk_widget_destroy (dlg);
}

static void
glade_helper_bad_columns (const char *filename, const char *widget,
			  GType type, int columns)
{
	GtkWidget *dlg;
	char *typestring;
	const char *typename;

	if (type != 0)
		typename = g_type_name (type);
	else
		typename = NULL;

	if (typename == NULL)
		typestring = g_strdup_printf (" (%s)", typename);
	else
		typestring = g_strdup ("");
	
	dlg = gtk_message_dialog_new (NULL /* parent */,
				      0 /* flags */,
				      GTK_MESSAGE_ERROR,
				      GTK_BUTTONS_CLOSE,
				      _("An error occured while loading the user "
					"interface\nelement %s%s from file %s.\n"
					"CList type widget should have %d columns.\n"
					"Possibly the glade interface description was "
					"corrupted.\n"
					"%s cannot continue and will exit now.\n"
					"You should check your "
					"installation of %s or reinstall %s."),
				      widget,
				      typestring,
				      filename,
				      columns,
				      PACKAGE,
				      PACKAGE,
				      PACKAGE);

	g_free (typestring);

	g_warning (_("Glade file is on crack! Make sure the correct "
		     "file is installed!\nfile: %s widget: %s "
		     "expected clist columns: %d"),
		   filename, widget, columns);

	gtk_dialog_run (GTK_DIALOG (dlg));
	gtk_widget_destroy (dlg);
}

static void
glade_helper_no_interface (const char *filename)
{
	GtkWidget *dlg;
	
	dlg = gtk_message_dialog_new (NULL /* parent */,
				      0 /* flags */,
				      GTK_MESSAGE_ERROR,
				      GTK_BUTTONS_CLOSE,
				      _("An error occured while loading the user "
					"interface\nfrom file %s.\n"
					"Possibly the glade interface description was "
					"not found.\n"
					"%s cannot continue and will exit now.\n"
					"You should check your "
					"installation of %s or reinstall %s."),
				      filename,
				      PACKAGE,
				      PACKAGE,
				      PACKAGE);
	g_warning (_("No interface could be loaded, BAD! (file: %s)"),
		   filename);

	gtk_dialog_run (GTK_DIALOG (dlg));
	gtk_widget_destroy (dlg);
}

/**
 * glade_helper_find_glade_file:
 * @file:  glade filename
 *
 * Description:  Finds a glade file in the same directories that
 * glade_helper would look in.  A utility if you use glade elsewhere in your
 * application to make using glade simpler.
 *
 * Returns:  Newly allocated string with the full path, or %NULL
 * if not found.
 **/
char *
glade_helper_find_glade_file (const char *file)
{
	g_return_val_if_fail (file != NULL, NULL);

	if (ve_search_gnome_dirs)
		return ve_find_file (file, ve_glade_directories);
	else
		return ve_find_file_simple (file, ve_glade_directories);
}

/**
 * glade_helper_add_glade_directory:
 * @directory:  directory with glade files
 *
 * Description:  Add a standard glade directory to search for
 * glade files.
 **/
void
glade_helper_add_glade_directory (const char *directory)
{
	ve_glade_directories = g_list_append (ve_glade_directories,
					      g_strdup (directory));
}

/**
 * glade_helper_seach_gnome_dirs:
 * @search_gnome_dirs:  boolean
 *
 * Description:  Sets if the gnome directories are searched.  Useful if
 * your program does not use gnome_program_ and you don't want glade_helper
 * to invoke gnome_program initialization by mistake.  This is because
 * it is possible for glade helper to try to use gnome_program_ routines
 * by default.
 **/
void
glade_helper_search_gnome_dirs (gboolean search_gnome_dirs)
{
	ve_search_gnome_dirs = search_gnome_dirs;
}

