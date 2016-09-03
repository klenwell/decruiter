"""
# Pages Controller
"""
from controllers import app, render_template


#
# Home Pages
#
@app.route('/', methods=['GET'])
def pages_home():
    return render_template('pages/home.html')
