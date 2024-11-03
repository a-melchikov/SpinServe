# SpinServe

Асинхронный веб-сервер на Python.

## Пример использования

```python
from spinserve.server import SpinServe

app = SpinServe()

@app.route("/hello")
async def hello(request):
    return "HTTP/1.1 200 OK\nContent-Type: text/plain\n\nHello user!"

if __name__ == "__main__":
    app.run()
```
