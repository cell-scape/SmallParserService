#! /usr/bin/env pypy3
# -*- coding: utf-8 -*-

import asyncio
from quart import Quart

app = Quart(__name__)


@app.route("/")
async def index():
    return "Hello world!"


if __name__ == "__main__":
    asyncio.run(app.run_task())
