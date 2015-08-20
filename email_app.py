from flask import Flask, render_template, request, redirect

from ml.summarizer import summarize_email
from ml.classifier import classify, categories
from ml.training_set_util import load_training_set, save_training_set, build_training_set_from_text

classified = None
count = 0
cached_training_set = []
sender, subject, email_text = None, None, None


def __init__(self):
    self.__count__ = 0
    self.cached_training_set = []
    self.classified = None


app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/emailsubmit', methods=['POST'])
def email_submit():
    global classified, sender, subject, email_text
    values = request.values
    _from, _to, _subject, _email_text = values['from'], values['to'], values['subject'], values['email_text']
    _email_text = _email_text.replace('\r\n', ' ').replace('\n', ' ').replace('\t', ' ')
    category = classify(_email_text, sender=_from, subject=_subject)
    classified = category
    summary = summarize_email(_email_text, sender=_from)
    sender, subject, email_text = _from, _subject, _email_text
    return render_template('result.html',
                           sender=sender,
                           to=_to,
                           subject=subject,
                           body=email_text,
                           classified='Email Category: {}'.format(category),
                           summary=summary)


@app.route('/addtotrain', methods=['POST'])
def add_to_train():
    global count, cached_training_set, classified, sender, subject, email_text
    values = request.values
    if classified is None:
        return redirect('/')
    category = int(values['category'])
    inv_categories = {v: k for k, v in categories.items()}
    category = inv_categories[classified] if category == 0 else category
    temporary = build_training_set_from_text(text=email_text, category=category, sender=sender, subject=subject)
    cached_training_set += temporary
    count += 1
    if count >= 2:
        training_set = load_training_set()
        training_set += cached_training_set
        save_training_set(training_set)
        print 'Training set updated and persisted with new items'
        count, cached_training_set, classified = 0, [], None
    return redirect('/')


if __name__ == "__main__":
    app.run()
