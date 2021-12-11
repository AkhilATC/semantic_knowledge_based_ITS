import eel
from cache_store import HistoryManager
from parser import OwlCustomParser as CoreParser


@eel.expose
def init_session():
    print("----- in init --")
    parser = CoreParser()
    output = parser.initiate_chat()
    # print(output)
    return output


@eel.expose
def fetch_info(node):
    print(f"----- in fetch info -- {node}")
    parser = CoreParser()
    output = parser.construct_query(node)
    return output


eel.init("ui")
# Start the index.html file
eel.start('index.html', size=(600, 400))
