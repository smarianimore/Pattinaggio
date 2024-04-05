from flask import Flask

# The __name__ variable passed to the Flask class is a Python predefined variable, which is set to the name of the
# module in which it is used. Flask uses the location of the module passed here as a starting point when it needs to
# load associated resources such as template files
skating_app = Flask(__name__)

# The bottom import is a well known workaround that avoids circular imports, a common problem with Flask applications.
# You are going to see that the routes module needs to import the app variable defined in this script, so putting one
# of the reciprocal imports at the bottom avoids the error that results from the mutual references between these two
# files.
from skating_app import routes
