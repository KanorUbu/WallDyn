#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import sys
import urllib
import getopt
import os
import commands
import re
from xml.dom.minidom import Document
from xml.dom import minidom
from math import cos, sin , sqrt, asin, radians
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    stream=sys.stderr)

#Fonction
def usage():
   print "Logiciel pour mettre en place un fond écran en fonction de la météo et de l\'heure \n ------Commande Possible ------- \n -h,--help pour obtenir cet aide \n -v,-ville pour définir la variable correspondant à votre ville grace au site weather.com \n -i,--images pour définir le dossier ou se trouve le pack d\'image \n -a,--ajouter pour rajouter dans le cron \n -e,--enlever pour supprimer dans le cron "


# association entre un numero d'icone et un nom de fichier a partir du fichier "map"
def transform_weather_filename_from_icon_number(icon,directory_img):
   logging.debug(icon)
   name = "snow"

   # on cherche le numero de l'icone dans notre cartographie
   for i in open(os.path.join(sys.path[0],"map"),'r').xreadlines() :
      val = i.split('\t')
      if (int(val[0])) == icon :
         name = val[1].strip('\n').strip('\r').strip()
         break

   #    temps = ["storm","storm","storm","storm","storm","snow","rain","snow","rain","rain",
   #             "rain","shower","shower","snow","snow","snow","snow","rain","rain","fog",
   #             "fog","fog","fog","cloudy","cloudy","cloudy","cloudy","cloudy","cloudy","partly_cloudy",
   #             "partly_cloudy","sunny","sunny","fair","fair","rain","sunny","storm","storm","storm",
   #             "shower","snow","snow","snow","partly_cloudy","shower","snow","shower"]

   try:
      path = os.path.join(directory_img , name)
   except:
      path = os.path.join(directory_img ,"snow")
   return path



def calculeD(lat1,lon1,lat2,lon2):
   R = 6367000
   d = 2 * R * asin(sqrt( pow( sin((lon1 - lon2) / 2 ),2)  + cos(lon1) * cos(lon2) * pow( sin((lat1 -lat2)/2),2)))
   return d

def calcule_distance(lon1,lat1):
   lat1 = radians(float(lat1))
   lon1 = radians(float(lon1))
   listville = []

   for numeroLigne,ligne in enumerate(open(os.path.join(sys.path[0],"liste-ville"),'r').xreadlines()):
      try:
         lat2 = radians(float(ligne.split(":")[3]))
         lon2 = radians(float(ligne.split(":")[4]))
      except:
         pass
      d = calculeD(lat1,lon1,lat2,lon2)

      turple = (ligne.split(":")[0:2],d)
      listville.extend([turple])

   listville.sort(lambda a,b : cmp (a[1],b[1]))
   return listville[0]



##### prettyprint sans rajouter des espaces la ou il ne faut pas #####
def myprettyprint(doc, indent="\t"):
   lines = doc.toprettyxml(indent).splitlines()
   linesep = ""
   ret = ""
   nextshouldbestripped = 0
   for l in lines :
      if l.strip().startswith('<'):
         if nextshouldbestripped == 1 :
            ret = ret + linesep + l.strip(indent)
            nextshouldbestripped = 0
         else:
            ret = ret + linesep + l
         linesep = "\n"
      else:
         ret = ret + l.strip(indent)
         linesep = ""
         nextshouldbestripped = 1
   return ret
######################################################################



################################################################################################################################################################
def main(refcity,dir_xml,dir_img):
   #Récupération des données
   the_weather = Weather(refcity)
   sunrise = the_weather.sunrise()
   sunset = the_weather.sunset()
   logging.debug("Sunrise : " + str(sunrise))
   logging.debug("Sunset  : " + str(sunset))
   #Relation entre condition métérologique et nom du fichier
   icon = the_weather.icon_today()
   logging.debug(refcity)
   if (icon >= 0 and icon <= 47) :
      fileimage = transform_weather_filename_from_icon_number(icon,dir_img)
      logging.debug(fileimage)
      #Génération du fichier xml
      doc = CreateXml(fileimage, sunrise, sunset).doc
      #Enregistrement dans le fichier background.xml
      f = open(os.path.join(dir_xml,'newbackground.xml'), 'w')

      f.write(myprettyprint(doc, "   "))
      f.close()

################################################################################################################################################################



# Classe permettant la modication du cron
class ToolCron():
   def __init__(self):
      self.crontab = commands.getoutput("crontab -l")
      l = self.crontab.split()
      if (len(l) > 0) :
         # cas special ou le crontab est vide : dans ce cas le premier mot retourne par crontab -l est 'no'
         if (l[0] == "no"):
            self.crontab = ""
            logging.debug("No crontab before")
   def status(self,programme):
      result = "\n".join([ em for em in self.crontab.split('\n') if re.search(programme,em)])
      return result

   def add(self,newcron):
      f = file("/tmp/cron","w")
      result = ""
      if (self.crontab == ""):
         result = newcron
      else:
         result = self.crontab +'\n' + newcron

      f.write(result)
      f.close()
      commands.getoutput("crontab /tmp/cron")
      self.crontab = commands.getoutput("crontab -l")
      commands.getoutput("rm -f /tmp/cron")
      logging.debug("new cron : " + self.crontab)

   def delete(self,programme):
      result = "\n".join([ em for em in self.crontab.split('\n') if re.search(programme,em) == None])
      f = file("/tmp/cron","w")
      f.write(result)
      f.close()
      commands.getoutput("crontab /tmp/cron")
      self.crontab = commands.getoutput("crontab -l")
      commands.getoutput("rm -f /tmp/cron")

   def replace(self,programme,newcron):
      self.delete(programme)
      logging.debug("delete cron  :" + programme)
      self.add(newcron)
      logging.debug("add cron   :" + newcron)

# Classe générant le document xml
class CreateXml():
   def __init__(self,path, sunrise, sunset):
      self.doc = Document()
      # Creation de la balise background
      self._background = self.doc.createElement("background")
      self.doc.appendChild(self._background)
      # Creation de la balise starttime
      self._starttime = self.doc.createElement("starttime")
      self._background.appendChild(self._starttime)
      # Creation des noeuds de startime
      today = datetime.date.today()
      self._createN(self._starttime,"year", str(today.year))
      self._createN(self._starttime,"month", str(today.month))
      self._createN(self._starttime,"day", str(today.day))
      # TOCHECK
      # Bug de gnome chez moi? je dois commencer a 1 heure, et faire dans la suite comme ci cela etait 0h.
      # sinon au lieu d'avoir un apres midi (2.jpg) jusqu'a 5pm, je l'ai jusqu'a 4pm (pb heure gmt?)
      self._createN(self._starttime,"hour","1")
      self._createN(self._starttime,"minute","00")
      self._createN(self._starttime,"second","00")

      if (sunrise >= Hour(11,0)) :
         sunrise = Hour(11,0)
      elif (sunrise <= Hour(2,30)) :
         sunrise = Hour(2,30)

      if (sunset <= Hour(15,0)) :
         sunset = Hour(15,0)
      elif (sunset >= Hour(22,0)) :
         sunset = Hour(22,0)

      # 2h30 <= sunrise <= 11h
      # 15h <= sunset <= 22h

      t1 = sunrise.addHour(-1,-30)

      t2 = sunrise

      t3 = sunrise.addHour(1,30)

      t4 = Hour(13,0)

      t5 = sunset.addHour(-1,-30)

      t6 = sunset

      t7 = sunset.addHour(1,30)

      t8 = Hour(0,0)


      self._createNStatic(str(t8.DelayUntil(t1)),  path + "4.jpg")

      self._createNTransition(str(t1.DelayUntil(t2)), path + "4.jpg", path + "1.jpg")

      self._createNStatic(str(t2.DelayUntil(t3)),  path + "1.jpg")

      self._createNTransition(str(t3.DelayUntil(t4)), path + "1.jpg",path + "2.jpg")

      self._createNStatic(str(t4.DelayUntil(t5)),  path + "2.jpg")

      self._createNTransition(str(t5.DelayUntil(t6)), path + "2.jpg",path + "3.jpg")

      self._createNStatic(str(t6.DelayUntil(t7)),  path + "3.jpg")

      self._createNTransition(str(t7.DelayUntil(t8)), path + "3.jpg",path + "4.jpg")

   def _createNoeud(self,nom):
      noeud = self.doc.createElement(nom)
      return noeud

   def _createN(self,pere,fils,valeur=""):
      fils = self._createNoeud(fils)
      texte = self.doc.createTextNode(valeur)
      fils.appendChild(texte)
      pere.appendChild(fils)

   def _createNStatic(self,durer,fichier):
      static = self.doc.createElement("static")
      self._background.appendChild(static)
      self._createN(static,"duration",durer)
      self._createN(static,"file",fichier)

   def _createNTransition(self,durer,fichier1,fichier2,mode="overlay"):
      transition = self.doc.createElement("transition")
      transition.setAttribute("type", mode)
      self._background.appendChild(transition)
      self._createN(transition,"duration",durer)
      self._createN(transition,"from",fichier1)
      self._createN(transition,"to",fichier2)




class Hour():
   def fromStr(self, val):
      value1 = val.split(':')
      value2 = value1[1].split()

      self.hour = int(value1[0])
      self.minute = int(value2[0])
      if (value2[1] == "PM" and self.hour != 12):
         self.hour = self.hour + 12
      if (value2[1] != "PM" and self.hour == 12):
         self.hour = 0
      self.hour = divmod(self.hour,24)[1]
      self.minute = divmod(self.minute,60)[1]

   def __init__(self, hour, minute):
      self.hour = divmod(hour,24)[1]
      self.minute = divmod(minute,60)[1]

   def toDelay(self):
      return self.hour*3600 + self.minute*60

   def __lt__(self, other):
      return (self.toDelay() < other.toDelay())

   def __le__(self, other):
      return (self.toDelay() <= other.toDelay())

   def __eq__(self, other):
      return (self.toDelay() == other.toDelay())

   def __ne__(self, other):
      return (self.toDelay() != other.toDelay())

   def __gt__(self, other):
      return (self.toDelay() > other.toDelay())

   def __ge__(self, other):
      return (self.toDelay() >= other.toDelay())

   def addHour(self, hour, minute):
      nbsec = divmod(3600*hour+60*minute+self.toDelay(), 3600*24)[1]

      ret = divmod(nbsec, 3600)
      hour = ret[0]
      minute = divmod(ret[1], 60)[0]
      return Hour(hour, minute)



   def DelayUntil(self, other):
      ret = other.toDelay() - self.toDelay()
      if (ret < 0):
         ret = ret + 3600*24
      return ret

   def getHour(self):
      return self.hour

   def getMinute(self):
      return self.minute

   def __str__(self):
      return str(self.hour) + " h " + str(self.minute) + " min"

#Récupération des données méterologiques à partir du site weather.com
class Weather():
    def __init__(self,refcity,nb_day = '4'):
        self.error = [0,"Problem of connexion with weather.com",'Invalid location provided.','No location provided.']
        try:
            url = 'http://xml.weather.com/weather/local/'+ refcity + '?cc=*&unit=m'
            self.meteoxml = urllib.urlopen(url)
        except (IOError, OSError):
            self.error[0] = 1
            sys.exit(2)
        self.document = minidom.parse(self.meteoxml)
        self.meteoxml.close()
        try:
            if self._recup([('error','0'),('err','0'),'0']) == u'Invalid location provided.':
                self.error[0] = 2
            elif self._recup([('error','0'),('err','0'),'0']) == u'No location provided.':
                self.error[0] = 3
        except:
            pass
        if self.error[0] != 0:
            print self.error[self.error[0]]
            sys.exit(2)

    def sunrise(self):
        result = Hour(0,0)
        result.fromStr(self._recup([('loc','0'),('sunr','0'),'0']))
        return result

    def sunset(self):
        result = Hour(0,0)
        result.fromStr(self._recup([('loc','0'),('suns','0'),'0']))
        return result

    def _recup(self,data_for_parse):
        parse = 'self.document.' + "".join([ """getElementsByTagName('%s')[%s].""" % (k,v)
              for k,v in data_for_parse[:-1]]) + 'childNodes[%s].nodeValue' % data_for_parse[-1]
        result = eval(parse)
        return result

    def w_today(self):
        result = self._recup([('cc','0'),('t','0'),'0'])
        return result

    def icon_today(self):
        result = int(self._recup([('cc','0'),('icon','0'),'0']))
        return result

    def moon(self):
        result = self._recup([('cc','0'),('moon','0'),('t','0'),'0'])
        return result

    def w_day(self,nb_day,d_or_n):
        #nb_day donne la météo x jour aprés la date actuel
        #d_or_n météo du jour 0 méteo de nuit 1
        result = self._recup([('dayf','0'),('day',nb_day),('part',d_or_n),('t','0'),'0'])
        return result

    def city(self):
        result = self._recup([('loc','0'),('dnam','0'),'0']).split(",")[0]
        return result

    def country(self):
        result = self._recup([('loc','0'),('dnam','0'),'0']).split(",")[1]
        return result

    def lon(self):
        result = self._recup([('loc','0'),('lon','0'),'0'])
        return result

    def lat(self):
        result = self._recup([('loc','0'),('lat','0'),'0'])
        return result

    def searchLocation(self,search):
        self.error = [0,"Problem of connexion with weather.com",'Invalid location provided.','No location provided.']
        try:
            location = urllib.urlopen('http://xoap.weather.com/search/search?where=%s' % search)
        except (IOError, OSError):
            self.error[0] = 1
            sys.exit(2)
        document = minidom.parse(location)
        self.meteoxml.close()
        try:
            if self._recup([('error','0'),('err','0'),'0']) == u'Invalid location provided.':
                self.error[0] = 2
            elif self._recup([('error','0'),('err','0'),'0']) == u'No location provided.':
                self.error[0] = 3
        except:
            pass


if __name__ == '__main__':
   try:
      opts, args = getopt.getopt(sys.argv[1:], "haev:i:x:", ["help","ajouter","enlever","ville=","images=","xml="])
   except getopt.error,err:
      usage()
      sys.exit(2)
   cron = 3
   for opt, arg in opts:
      if opt in ("-h","--help"):
         usage()
         sys.exit(2)
      elif opt in ("-a","--ajouter"):
         cron = 1
      elif opt in ("-e","--enlever"):
         cron = 2
      elif opt in ("-v","--ville"):
         refcity = arg
      elif opt in ("-i","--images"):
         dir_img  = arg
      elif opt in ("-x","--xml"):
         dir_xml = arg

   # Enregistrement ou suppression  dans le cron
   if cron == 3: # laisser en l'état
      pass
   elif cron == 1: # enregistrement dans le crontab
      objetcron = ToolCron()
      lignecron =  " ".join([ em for em in sys.argv[1:] if (em in ( '-a','--ajouter','-e','--enlever','-h','--help')) == False ])
      crontab = objetcron.crontab + "\n*/15 * * * *  "+ sys.executable +" "+ os.path.join(fileprog,sys.argv[0]) +"  "+ lignecron +"\n"
      print "Rajouter la ligne suivante dans votre crontab \n*/15 * * * *  "+ sys.executable +" "+ os.path.join(fileprog,sys.argv[0]) +"  "+ lignecron + "?\n Taper Yes ou No pour valider"
      resultat = raw_input()
      if resultat.lower() == 'yes':
         objetcron.replace("background",crontab)
         print 'Crontab modifié'
      else :
         sys.exit(2)
   elif cron == 2: # suppresion dans le crontab
          ToolCron().delete("background")
          print "Cron de "+sys.argv[0]+ " enlevé"
          sys.exit(2)


   main(refcity,dir_xml,dir_img)


