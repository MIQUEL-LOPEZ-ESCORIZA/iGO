import networkx as nx
import osmnx as ox
import random
import igo
import os
import datetime
from staticmap import StaticMap, CircleMarker
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import datetime

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 800
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

if not igo.exists_graph(GRAPH_FILENAME):
    graph = igo.download_graph(PLACE)
    igo.save_graph(graph, GRAPH_FILENAME)
else:
    graph = igo.load_graph(GRAPH_FILENAME)

highways = igo.download_highways(HIGHWAYS_URL)

update_time = datetime.datetime.now()
congestions = igo.download_congestions(CONGESTIONS_URL)

igraph = igo.build_igraph(graph, highways, congestions)


def start(update, context):
    """ This is our initial function, which does nothing more than printing a introduction phrase on the chat. """

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="On vols que et porti? \n Envia'm la teva localització i on vols arribar!")


def authors(update, context):
    """ This function prints on the chat the authors of the project. """

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Miquel López i Martí Farré, estudiants de Ciència i Enginyeria de Dades, UPC")


def help(update, context):
    """ This function is for the user to know which functions the bot has.
        The user can call the functions pressing on the message. """

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sóc un bot amb comandes /start, /help, /authors, /go, /where i /pos.\n T'ajudaré a arribar on vulguis de Barcelona.")


def where(update, context):
    """ This function gets the user position through the Telegram location function.
        It also prints a map with this location. """

    try:
        lat, lon = update.message.location.latitude, update.message.location.longitude
        position = [lat, lon]
        context.user_data['origin'] = ox.geocoder.geocode(position)
        fitxer = "%d.png" % random.randint(1000000, 9999999)
        mapa = StaticMap(500, 500)
        mapa.add_marker(CircleMarker((lon, lat), 'blue', 10))
        imatge = mapa.render()
        imatge.save(fitxer)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ets aquí.")
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(fitxer, 'rb'))
        os.remove(fitxer)
    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='💣')


def update(context):
    """ This is an auxiliar function for the /go method. It updates the congestions on the map. """

    now = datetime.datetime.now()
    update_time = now
    congestions = igo.download_congestions(CONGESTIONS_URL)
    igraph = build_igraph(graph, highways, congestions)
    return igraph


def igraph_must_update(context):
    """ This function is used to know whether the congestions must be updated or not.
        The congestions update if 5 minuts have passed until last update. """

    now = datetime.datetime.now()
    return now > update_time + datetime.timedelta(minutes=5)


def destination_position(update, context):
    """ This auxiliar function gets the position of the user destination. """

    try:
        dst = update.message.text[4:]
        context.user_data['destination'] = ox.geocoder.geocode(dst + ', Barcelona')
    except:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="No has enviat el destí! \n Afegeix-lo a continuació de la comanda /go.")


def pos(update, context):
    """ This function is used to define a starting position that differs from your
        current location. """

    try:
        pos = update.message.text[5:]
        context.user_data['origin'] = ox.geocoder.geocode(pos + ', Barcelona')
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Ets a " + str(pos))

        """ context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Ets a ")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=context.user_data['origin']) """
    except:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="No has enviat l'origen! \n Afegeix-lo a continuació de la comanda /pos.")


def go(update, context):
    """ This is the bot main function. It returns a picture of the shortest path between
        the user location (real or defined with the /pos command). It uses iGo functions
        to do so. """

    destination_position(update, context)
    try:
        orig_long, orig_lat = context.user_data['origin']
        dst_long, dst_lat = context.user_data['destination']
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Segueix aquest camí per arribar al teu destí!")
    except:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="No has dit on ets!\n Utilitza les comandes /where o /pos i defineix la teva posició.")
    global igraph
    if igraph_must_update(context):
        igraph = update(context)
    ipath = igo.get_shortest_path_between_coords(
        igraph, orig_long, orig_lat, dst_long, dst_lat)
    igo.plot_path(igraph, ipath, SIZE)
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('shortest_path.png', 'rb'))


TOKEN = open('token.txt').read().strip()

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('authors', authors))
dispatcher.add_handler(MessageHandler(Filters.location, where))
dispatcher.add_handler(CommandHandler('pos', pos))
dispatcher.add_handler(CommandHandler('go', go))

updater.start_polling()
