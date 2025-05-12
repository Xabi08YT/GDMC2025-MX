import webbrowser

def launch_visualization_server():
    url = "http://127.0.0.1:5000"

    webbrowser.open(url, new=0, autoraise=True)

    import visualizationServer.server as srv

if __name__ == "__main__":
    launch_visualization_server()