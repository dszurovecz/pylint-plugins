"""Module docstring"""

import logging
import os
import re
from random import choice

test_list=[]
RESULT = ", ".join(["apple", "banana", "cherry"])
logging.info("test")
os.getcwd()
re.search(".*", "hello")
test_list.append("test")
"HELLO".split(",")
letters = ["A", "C", "D"]
TAG = "tag_%s" % ("".join(choice(letters) for i in range(5))) # pylint: disable=C0209
# "table_%s" % ("".join(random.sample(string.ascii_lowercase, 5)))