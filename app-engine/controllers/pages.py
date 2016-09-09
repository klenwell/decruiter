"""
# Pages Controller
"""
from datetime import datetime, timedelta

from controllers import app, render_template
from models.recruiter_email import RecruiterEmail


#
# Home Pages
#
@app.route('/', methods=['GET'])
def pages_home():
    a_month_ago = datetime.now() - timedelta(days=30)
    recruitments = RecruiterEmail.s_sent_since(a_month_ago)
    recruiter_count = len(set([r.recruiter_email for r in recruitments]))
    return render_template('pages/home.html',
                           recruitment_count=len(recruitments),
                           recruiter_count=recruiter_count,
                           cutoff=a_month_ago)
