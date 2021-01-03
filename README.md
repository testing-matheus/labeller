# ETIQUETADOR DE DETECCIÓN DE OBJETOS
[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

El siguiente repo tiene un etiquetador construido para tareas de detección de objetos:
  - Esta construido para etiquetar imagenes que son provenientes de un video, utilizando trackers para mejorar la efectividad con la que se realiza el etiquetado
  - Se deben agregar las diferentes clases en config/class_list.txt las cuales serán mostradas en etiquetador
  - Posee los siguientes trackers csrt, boosting, mil, kcf, medianflow, tld, mosse (default csrt)
  - La salida del etiquetador es un .xml con las clases presentes en la imagen y sus bounding box
  - La carpeta imagen es la que va a leer el etiquetador y es donde deben estar las imagenes, de preferencia en formato .jpg

### SETUP 
Pasos a seguir para comenzar a etiquetar

```sh
$ git clone https://github.com/testing-matheus/labeller.git
$ cd labeller
$ echo agregar las imagenes en la carpeta imagen en formato .jpg de preferencia
$ echo agregar las clases que estan presentes en las imagenes en la carpeta config/class_list.txt
$ pip install opencv-contrib-python==3.4.5.20
$ pip install PyQt5==5.15.2
$ python main.py
Comienza a etiquetar
```
Una buena metodología en el caso de tener una clase por imagen es tener las clases separadas por carpetas, te hará avanzar más rápido y los trackers serán más efectivos, en el caso de que no quieras usar trackers usa el DoNothing, puede ser el caso en el que el tracker no sea la opción más rápida debido a que las imagenes son muy distintas entre si.

Agradecimientos a PSINet.
