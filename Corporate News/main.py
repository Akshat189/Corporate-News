from bs4 import BeautifulSoup
import requests
import xml
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import psycopg2
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data-collection.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///data-collection.db")
db = SQLAlchemy(app)
Bootstrap(app)

class Data(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)
# db.create_all()
    # db.session.commit()

class CompanyNameForm(FlaskForm):
    name = StringField("Company")
    submit = SubmitField("Done")


@app.route("/", methods=['GET', 'POST'])
def get_data():
    form = CompanyNameForm()
    if form.validate_on_submit():
        company = form.name.data
        company_list = []
        id_data = db.session.query(Data.id).all()
        company_list = [str(column) for column in id_data]
        print(type(company_list[0]))
        print(company_list)

        company_id = f"('{company}',)"
        print(company_id)
        print(type(company_id))



        url = f"https://www.thestreet.com/quote/{company}#news-0"
        response = requests.get(url).content

        soup = BeautifulSoup(response, 'html.parser')
        # print(soup)
        all_title = soup.find_all(class_="m-ellipsis--text")
        all_summary = soup.find_all('p', class_="m-card--body")
        all_links = soup.find_all('a', id="Title")
        titles = []
        summaries = []
        for title in all_title:
            titles.append(title.text)

        for summary in all_summary:
            summaries.append(summary.text)

        title_string = ', '.join(titles)
        summary_string = ', '.join(summaries)



        length = range(len(titles))

        if company_id in company_list:
            for comp in company_list:
                if comp == company_id:
                    data_to_update = Data.query.get(company)
                    data_to_update.title = title_string
                    data_to_update.description = summary_string
                db.session.commit()
        else:
            db.session.add(
                Data(
                    id=company,
                    title=title_string,
                    description=summary_string,
                )
            )
            db.session.commit()


        return render_template("news.html", titles=titles, summaries=summaries, length=length)

    return render_template("index.html", form=form)

@app.route("/all", methods=['GET', 'POST'])
def get_all_news():
    all_news = db.session.query(Data).all()
    news_list = []
    for news in all_news:
        data = {
            'id': news.id,
            'title': news.title,
            'description': news.description
        }
        # news_list.append(data)
    # json_news = {"news": news_list}
    json_news = {"news": data}

    return jsonify(news = json_news['news'])



if __name__ == '__main__':
    app.run(debug=True)

