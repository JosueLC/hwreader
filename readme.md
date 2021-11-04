# HWReader

Esta aplicación lee un archivo de configuración de hardware de un plc en un proyecto de PCS 7 o Step7 (*.cfg) y genera un archivo de excel detallando las redes profibus, los dispositivos, módulos y señales en cada uno de ellos.

## Requisitos:
Necesita un archivo de configuración de hardware de Step7. La ruta del archivo debe ser especificada en la línea de comandos.
Python 3.9 o superior.
El archivo "requirements.txt" contiene las dependencias necesarias para ejecutar la aplicación. Se sugiere instalar las dependencias con el comando "pip install -r requirements.txt" en un ambiente virtual de python.

## Ejemplo de ejecución:
```sh
python main.py /home/user/documents/plc/hw.cfg
```

*This application reads a hardware configuration file of a plc in a PCS 7 or Step7 project (\*.cfg) and generates an excel file detailing the profibus networks, devices, modules and signals in each one of them.*

## Requisites:
Need a hardware configuration file of Step7. The path of the file must be specified in the command line.
Python 3.9 or superior.
The file "requirements.txt" contains the dependencies necessary to run the application. It is recommended to install the dependencies with the command "pip install -r requirements.txt" in a virtual environment of python.

## Example of execution:
```sh
python main.py /home/user/documents/plc/hw.cfg
```
