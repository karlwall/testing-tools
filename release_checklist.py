"""
Release to testing test script.

"""

# pip install sst
# not ready for use yet
# http://testutils.org

import logging
import random
import urlparse


from sst.actions import * 

SERVER = "http://local.appspot.com:8000"
SIGNUP_PATH = "signup"


url = urlparse.urljoin(SERVER, SIGNUP_PATH)

go_to(url)
assert_dropdown("id_name")
click_element("id_name")
set_dropdown_value("id_name", "Building and Trade")
assert_dropdown_value("id_name", "Building and Trade")
assert_displayed("industries-view")
industry_links = get_elements(tag="a")
assert len(industry_links) > "No industry links found"
industry_link = random.choice(industry_links)
logging.info("Selected link %s", industry_link)
click_link(industry_link)
assert_displayed("signup-content")
design_link = random.choice(get_elements_by_css("#design-display"))
logging.info("Selected link %s", design_link)
click_link(design_link)


