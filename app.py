import asyncio
from quart import Quart
from quart import render_template


app = Quart(__name__)


@app.route("/")
@app.route("/hello/")
@app.route("/hello/<name>")
async def index(name=None):
    """Landing page for test application."""
    return render_template('hello.html', name=name)


if __name__ == "__main__":
    asyncio.run(app.run_task())
