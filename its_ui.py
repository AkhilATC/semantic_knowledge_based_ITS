import eel
from cache_store import HistoryManager
from parser import OwlCustomParser as CoreParser


@eel.expose
def init_session():
    print("----- in init --")
    parser = CoreParser()
    output = parser.initiate_chat()
    print(output)
    return output

eel.init("ui")
# Start the index.html file
eel.start('index.html', size=(600, 400))
