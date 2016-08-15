## spacewalk-device42.py

Maintainer: Mark Mercado <mamercad@umflint.edu>

#### Overview

This script pushes four facts from Spacewalk (`Organization`, `Base Channel`,  `Activation Key` and `Registration Date`) into Device42. Naturally, these fields
must be created in Device42 as "custom fields". In the order listed, the first three are type `text` and the last is type `date`.

#### Usage

The usage is a little clunky right now, partly because of the way privileges work in Spacewalk (I need to do more research on this). Rename `spacewalk-device42.ini.sample` to `spacewalk-device42.ini` and update accordingly.

#### Python modules

```python
import arrow
import ConfigParser
import requests
import ssl
import sys
import xmlrpclib
```
