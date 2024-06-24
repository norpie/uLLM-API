def start(host, port, model_manager):
    import threading
    thread = threading.Thread(target=run, args=(host, port, model_manager))
    thread.start()

def run(host, port, model_manager):
    pass
