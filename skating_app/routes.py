from skating_app import skating_app


# A common pattern with decorators is to use them to register functions as callbacks for certain events. In this case,
# the @app.route decorator creates an association between the URL given as an argument and the function
@skating_app.route('/')
@skating_app.route('/index')
def index():
    return "Hello, World!"
