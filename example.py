from spinserve.server import SpinServe

app = SpinServe(
    host="localhost",
    port=8080,
)


@app.route("/hello")
async def hello(request):
    return "HTTP/1.1 200 OK\nContent-Type: text/plain\n\nHello from example!"


if __name__ == "__main__":
    app.run()
