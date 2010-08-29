#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys
import pygtk
pygtk.require('2.0')
import gtk
from newbackground import *

walldyn_version = "0.1"

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    stream=sys.stderr)

class Background(gtk.Assistant):
    """ Class permettant la création de l'interface"""


    def __init__(self):
        self.data = {"refcity":"","fileimage":"","filexml":""}
        self.page = {}
        self.final= {"cron":False,"generate":False}
        gtk.Assistant.__init__(self)

        self._addIntroPage()
        self._addRefCityPage()
        self._addPathPage()
        self._addLastPage()

        self.connect("delete_event", self._cb_delete_event)
        self.connect("close", self._cb_destroy)
        self.connect("cancel", self._cb_destroy)
        self.connect("destroy", self._cb_destroy)
        #self.connect("apply", self._cb_apply)
        #for pagename in self.pages.iterkeys():
          #  self.checkcompletion(pagename)
        self.show()

    def _addIntroPage(self):
        label = gtk.Label("""Interface pour installer un wallpaper dynamite suivant le temps qui passe et la météo""")
        self.page["intro"] = label
        label.set_line_wrap(True)
        label.show()
        self.append_page(label)
        self.set_page_title(label, "Introduction")
        self.set_page_type(label, gtk.ASSISTANT_PAGE_INTRO)
        self.set_page_complete(label, True)

    def _addRefCityPage(self):
        page = gtk.VBox(False, 10)
        self.page["city"] = page
        #self.pages["refcity"] = page
        page.set_border_width(5)
        page.show()
        self.append_page(page)
        self.set_page_title(page,"Détermination de la référence de la ville")
        self.set_page_type(page, gtk.ASSISTANT_PAGE_CONTENT)

        label = gtk.Label("Si vous habitez en France vous pouvez utiliser une des trois méthodes pour trouver votre ville.\n Si vous habitez dans un autre pays vous pouvez utiliser seulement la premiére méthode")
        label.set_line_wrap(True)
        label.show()
        page.pack_start(label, True, True, 0)

        table = gtk.Table(rows=3, columns=3, homogeneous=False)
        table.show()

        ##Reference de la ville ###
        label = gtk.Label("Référence de la ville")
        label.show()
        table.attach(label, 0, 1, 0, 1)
        entry_ref = gtk.Entry(max=8)
        entry_ref.show()
        table.attach(entry_ref, 1, 2, 0, 1)
        button_ref = gtk.Button("Valider")
        button_ref.show()
        table.attach(button_ref,2,3,0,1)

        ## Nom de la ville ###

        label = gtk.Label("Nom de la ville")
        label.show()
        table.attach(label, 0, 1, 1, 2)
        entry_city = gtk.Entry(max=30)
        # Create the completion object
        completion = gtk.EntryCompletion()
        # Assign the completion to the entry
        entry_city.set_completion(completion)
        # Create a tree model and use it as the completion model
        completion_model = self.__create_completion_model()
        completion.set_model(completion_model)
        # Use model column 0 as the text column
        completion.set_text_column(0)
        entry_city.show()
        table.attach(entry_city, 1, 2, 1, 2)
        button_city = gtk.Button("Valider")
        button_city.show()
        table.attach(button_city, 2, 3, 1, 2)

        ##Distance à la ville###
        label = gtk.Label("Longitude et latitude")
        label.show()
        table.attach(label, 0, 1, 2, 3)
        case = gtk.HBox(False, 10)
        case.show()
        entry_lon = gtk.Entry(max=8)
        entry_lon.show()
        case.pack_start(entry_lon, True, True, 0)
        entry_lat = gtk.Entry(max=8)
        entry_lat.show()
        case.pack_end(entry_lat, True, True, 0)
        table.attach(case, 1, 2, 2, 3)
        button_dist = gtk.Button("Valider")
        button_dist.show()
        table.attach(button_dist,2,3,2,3)

        page.pack_start(table)


        label.set_line_wrap(True)
        label_notify = gtk.Label("")
        label_notify.show()
        page.pack_end(label_notify, True, True, 0)
        button_city.connect("clicked",self._cb_entry_city, entry_city, label_notify, entry_ref, page, entry_lon, entry_lat)
        button_ref.connect("clicked",self._cb_entry_refcity,entry_city, label_notify, entry_ref, page, entry_lon, entry_lat)
        button_dist.connect("clicked",self._cb_entry_dist,entry_city, label_notify, entry_ref, page, entry_lon, entry_lat)

    def _addPathPage(self):
        page = gtk.VBox(False, 5)
        self.page["Path"] = page
        #self.pages["pathselection"] = page
        page.set_border_width(5)
        page.show()
        self.append_page(page)
        self.set_page_title(page,
                            "Chemins des différent dossier")
        self.set_page_type(page, gtk.ASSISTANT_PAGE_CONTENT)

        label = gtk.Label("Choisissez l'emplacement des dossiers")
        label.set_line_wrap(True)
        label.show()
        page.pack_start(label, True, True, 0)

        table = gtk.Table(rows=2, columns=2, homogeneous=False)
        table.show()
        label = gtk.Label("Dossier des images")
        label.show()
        table.attach(label, 0, 1, 0, 1)
        button = gtk.FileChooserButton("Choisissez le dossier")
        button.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        button.connect("selection-changed", self._cb_dir_image)
        button.show()
        table.attach(button, 1, 2, 0, 1)

        label = gtk.Label("Dossier de génération de background.xml")
        label.show()
        table.attach(label, 0, 1, 1, 2)
        button = gtk.FileChooserButton("Choisissez le dossier")
        button.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        button.connect("selection-changed", self._cb_dir_xml)
        button.show()
        table.attach(button, 1, 2, 1, 2)

        page.pack_end(table)


    def _addLastPage(self):
        page = gtk.VBox(False, 5)
        self.page["output"] = page
        page.set_border_width(5)
        page.show()
        self.append_page(page)
        self.set_page_title(page,
                           "Finalisation")
        self.set_page_type(page, gtk.ASSISTANT_PAGE_CONFIRM)
        self.set_page_complete(page, True)
        button = gtk.CheckButton("Si vous voulez générez directement le fichier xml cocher la case et changer le background.")
        button.show()
        page.pack_start(button)
        button.connect("toggled", self._cb_toggle, "generate")
        button = gtk.CheckButton("Si vous voulez lancer le programme avec le cron" )
        button.show()
        page.pack_start(button)
        button.connect("toggled", self._cb_toggle, "cron")
        label = gtk.Label('Quand vous avez finie votre configuration cliquer sur Appliquer')
        label.show()
        page.pack_end(label)
        self.connect("apply",self._cb_apply)

    def _cb_toggle(self, widget, donne):
          logging.debug("toggle  " + donne)
          self.final[donne] = widget.get_active()
          print widget.get_active()

    def _cb_dir_image(self, w):
        logging.debug("select dir image")
        self.data["fileimage"] = w.get_filename()
        self._check()

    def _cb_dir_xml(self, w):
        logging.debug("select dir xml")
        self.data["filexml"] = w.get_filename()
        self._check()

    def _check(self):
        logging.debug("check")

        if self.data["fileimage"] != '' and self.data["filexml"] != '':
            self.set_page_complete(self.page["Path"], True)
        else:
            self.set_page_complete(self.page["Path"], False)

    def _cb_delete_event(self, widget, event, data = None):
        logging.debug("delete_event")
        return False

    def _cb_destroy(self, widget, data = None):
        logging.debug("destroy")
        gtk.main_quit()

    def _cb_entry_refcity(self,widget,entry_city, label_notify, entry_ref, page, entry_lon, entry_lat):
        logging.debug("refcity")
        refcity = entry_ref.get_text()
        meteo = Weather(refcity)
        if meteo.error[0] != 0:
            label_notify.set_label(meteo.error[meteo.error[0]])
        else:
            label_notify.set_label('Référence valide' )
            city = meteo.city()
            lon = meteo.lon()
            lat = meteo.lat()
            entry_city.set_text(city)
            entry_lon.set_text(lon)
            entry_lat.set_text(lat)
            self.data["refcity"] = refcity
            self.data["city"] = city
            self.set_page_complete(page, True)

    def __create_completion_model(self):
        ''' Creates a tree model containing the completions.
        '''
        logging.debug("completion")
        store = gtk.ListStore(str)
        for numeroLigne,ligne in enumerate(open(os.path.join(sys.path[0],"liste-ville"),'r').xreadlines()):
            iter = store.append()
            store.set(iter , 0,  ligne.split(":")[1])
        return store


    def _cb_entry_city(self,widget,entry_city, label_notify, entry_ref, page, entry_lon, entry_lat):
        logging.debug("city")
        city = entry_city.get_text()
        for numeroLigne,ligne in enumerate(open( os.path.join(sys.path[0],"liste-ville"),'r').xreadlines()):
            if city == ligne.split(":")[1]:
                refcity = ligne.split(":")[0]
                lat = ligne.split(':')[3]
                lon = ligne.split(":")[4].strip('\n')
                entry_ref.set_text(refcity)
                entry_lat.set_text(lat)
                entry_lon.set_text(lon)
                self.data["refcity"] = refcity
                self.set_page_complete(page, True)

    def _cb_entry_dist(self,widget,entry_city, label_notify, entry_ref, page, entry_lon, entry_lat):
        logging.debug("dist")
        lon = entry_lon.get_text()
        lat = entry_lat.get_text()
        liste = calcule_distance(lon,lat)
        city = liste[0][0][1]
        refcity = liste[0][0][0]
        entry_city.set_text(city)
        entry_ref.set_text(refcity)
        label_notify.set_label('La ville la plus proche de votre coordonné est ' + city + " à une distance de   "+ str(liste[0][1])  )
        self.data["refcity"] = refcity
        self.set_page_complete(page, True)


    def _cb_apply(self, widget):
        if self.final["cron"]:
            logging.debug("add cron")
            objetcron = ToolCron()
            argument =  "-i \"" + self.data["fileimage"]+ "\" -x \"" +  self.data["filexml"]  + "\" -v " + self.data["refcity"]
            lignecron = "*/15 * * * *  "+ sys.executable +" \""+ os.path.join(sys.path[0],"newbackground.py\"") +"  "+ argument +"\n"
            objetcron.replace("background",lignecron)
        if self.final["generate"]:
            logging.debug("genrate xml")
            main(self.data["refcity"],self.data["filexml"],self.data["fileimage"])
            gconf = " gconftool-2 --type string --set /desktop/gnome/background/picture_filename '"+ os.path.join(self.data["filexml"] , "newbackground.xml") + "'"
            commands.getoutput(gconf)
            logging.debug("file background  : "+ gconf)

if __name__ == "__main__":
    Background()
    gtk.main()
