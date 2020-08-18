from flask import Flask, render_template, url_for
import os

app = Flask(__name__)


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('MathBattleMainPage.html', style_way=url_for('static', filename='css/styles.css'),
                           file_way=url_for('static', filename='MathBattle.rar'))


if __name__ == '__main__':
    main()
