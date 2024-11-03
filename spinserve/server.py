import asyncio
import socket
import sys

from watchdog.observers import Observer

from .auto_reload import ReloadHandler
from .routes import ROUTES


class SpinServe:
    """
    Application instance.
    """

    def __init__(
        self, host: str = "127.0.0.1", port: int = 8080, auto_reload: bool = False
    ) -> None:
        self.host = host
        self.port = port
        self.auto_reload = auto_reload

    def route(self, path):
        def decorator(func):
            ROUTES[path] = func
            return func

        return decorator

    async def handle_client(self, client_socket):
        try:
            request = await asyncio.get_event_loop().sock_recv(client_socket, 1024)
            request_line = request.decode("utf-8").splitlines()[0]
            path = request_line.split(" ")[1]
            handler = ROUTES.get(path)

            if handler:
                response = await handler(request)
            else:
                response = "HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\nRoute Not Found"

            await asyncio.get_event_loop().sock_sendall(
                client_socket, response.encode("utf-8")
            )

        except BlockingIOError:
            print("Ресурс временно недоступен, попробуйте позже.")
        except Exception as e:
            print(f"Ошибка при обработке клиента: {e}")
        finally:
            client_socket.close()

    async def _main(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            server_socket.setblocking(False)
            print(f"Сервер запущен на {self.host}:{self.port}")
        except OSError as e:
            print(f"Ошибка привязки сокета: {e}")
            return

        loop = asyncio.get_running_loop()
        while True:
            client_socket, client_address = await loop.sock_accept(server_socket)
            print(f"Подключение от {client_address}")
            asyncio.create_task(self.handle_client(client_socket))

    def start_auto_reload(self):
        command = f"python {sys.argv[0]}"
        event_handler = ReloadHandler(command)
        observer = Observer()
        observer.schedule(event_handler, path=".", recursive=True)
        observer.start()

        try:
            asyncio.run(self._main())
        except KeyboardInterrupt:
            observer.stop()
            observer.join()

    def run(self):
        if self.auto_reload:
            self.start_auto_reload()
        else:
            asyncio.run(self._main())
