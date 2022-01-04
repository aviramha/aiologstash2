# aiologstash2

[![image](https://travis-ci.org/aio-libs/aiologstash.svg?branch=master)](https://travis-ci.org/aio-libs/aiologstash)

[![image](https://codecov.io/gh/aio-libs/aiologstash/branch/master/graph/badge.svg)](https://codecov.io/gh/aio-libs/aiologstash)

[![image](https://badge.fury.io/py/aiologstash.svg)](https://badge.fury.io/py/aiologstash)

asyncio logging handler for logstash.

# Installation

``` shell
pip install aiologstash2
```

# Usage

``` python
import logging
from aiologstash2 import create_tcp_handler

async def init_logger():
     handler = await create_tcp_handler('127.0.0.1', 5000)
     root = logging.getLogger()
     root.setLevel(logging.DEBUG)
     root.addHandler(handler)
```

# Thanks

This is an actively maintained fork of [aio-libs'
aiologstash](https://github.com/aio-libs/aiologstash)

The library was donated by [Ocean S.A.](https://ocean.io/)

Thanks to the company for contribution.
