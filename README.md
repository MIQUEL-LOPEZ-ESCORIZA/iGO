# iGo. A Barcelona guide bot.

**Version 1.0.0**

Telegram bot to find the shortest path between two places in Barcelona.

Final Project for Algorismia i Programació II course - Grau en Ciència i Enginyeria de Dades, UPC.

---
This project was developed as our final project for AP2 course. It was meant to challenge us, get used to third party libraries and obviously, gain confidence when approaching big coding projects.
The main purpose of this project is to find the quickest way to travel by car between your location and a desired destination in the city of Barcelona. It can also be extrapolated to other cities. To make it user-friendly, a Telegram Bot is used to help with the interaction between the user and the code. This means the program can be used with both computers and phones.

---
# How to use it

To use our project, one must use the message app **Telegram**. There one goes to the chat with our bot and uses the commands to activate the functionality. The commands are */start, /help, /authors, /go, /pos* and */where*. To start it, one calls */start*, and */go*, adds its location and destination, and the program will find the shortest path.  If one needs more information about the commands, calling the */help* command is useful.

---
# Implementation

The project has been coded using Python, and uses the libraries *Osmnx, Networkx, Staticmap, Pickle, CSV, Urllib, Haversine, Collections, Sklearn, Random, Os, Easyinput, Datetime, telegram.ext and iGo itself.* The data used to create it comes from Osmnx (Barcelona city graph) and Ajuntament de Barcelona Open Data (Highways and congestions in the city of Barcelona). The decision to use all of it, apart from the fact our professors made us to use it, was due to Python's simplicity and wide libraries access.

---
# Contributors

- Miquel López Escoriza <miquel.lopez.escoriza@estudiantat.upc.edu> - Data Science Engineering & Physics Engineering Student
- Martí Farré Farrús <marti.farre.farrus@estudiantat.upc.edu> - Data Science Engineering Student
