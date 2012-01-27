"""
Release to testing test script.

"""

# pip install sst
# not ready for use yet

import urlparse


from sst.actions import assert_dropdown, assert_dropdown_value, click_element, go_to, set_dropdown_value

SERVER = "http://local.appspot.com:8000"
SIGNUP_PATH = "signup"


url = urlparse.urljoin(SERVER, SIGNUP_PATH)

go_to(url)
assert_dropdown("id_name")
click_element("id_name")
set_dropdown_value("id_name", "Building and Trade")
assert_dropdown_value("id_name", "Building and Trade")


