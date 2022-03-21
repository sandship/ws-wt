import websocket
import _thread as thread
import json
from time import sleep

class Websocket_Client():
    def __init__(self, host_addr):
        self.ws = websocket.WebSocketApp(host_addr,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open=self.on_open

    def on_message(self, ws, message):
        print("receive : {}".format(message))

    def on_error(self, ws, error):
        pass

    def on_close(self, ws):
        pass

    def on_open(self, ws):
        thread.start_new_thread(self.run, ())

    def run(self):
        print("sending msg")
        for i in range(100):
            print(f"sequence: {str(i).zfill(4)}")
            self.ws.send(json.dumps({"position": {"x": i, "y": i, "z": i}}).encode())
            sleep(1/100)
        print("received msg")
        self.ws.close()

    def run_forever(self):
        self.ws.run_forever()


HOST_ADDR = "ws://127.0.0.1:18080/"
ws_client = Websocket_Client(HOST_ADDR)
ws_client.run_forever()