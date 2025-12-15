from flask import Flask, render_template, request, session, redirect, url_for
from owlready2 import get_ontology
import random

app = Flask(__name__)
app.secret_key = "mysecretkey123" 

onto = get_ontology("CapitalsTutor.owl").load()

def load_country_capital_pairs():
    pairs = []

    for entity in onto.individuals():
       
        if onto.Country in entity.is_a or any(
            subclass in entity.is_a for subclass in [
                onto.AfricanCountry, onto.EuropeanCountry, onto.AsianCountry
            ]
        ):
           
            if hasattr(entity, "hasCapital") and entity.hasCapital:
                capital = entity.hasCapital[0]
                pairs.append((entity.name, capital.name))

    return pairs



PAIRS = load_country_capital_pairs()


@app.route("/")
def index():
    session["score"] = 0
    session["asked"] = []
    return render_template("index.html", total=len(PAIRS))



@app.route("/learn")
def learn():
    data = [{"country": c, "capital": k} for c, k in PAIRS]
    return render_template("learn.html", data=data)



@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    # When answer is submitted
    if request.method == "POST":
        user_answer = request.form["capital"].strip().lower()
        correct_answer = session["current_capital"].lower()

        result = (user_answer == correct_answer)

        if result:
            session["score"] += 1

        return render_template(
            "result.html",
            result=result,
            correct=session["current_capital"],
            score=session["score"]
        )

   
    remaining = [p for p in PAIRS if p[0] not in session["asked"]]

   
    if not remaining:
        return render_template(
            "index.html",
            finished=True,
            score=session["score"],
            total=len(PAIRS)
        )

   
    country, capital = random.choice(remaining)
    session["current_country"] = country
    session["current_capital"] = capital
    session["asked"].append(country)

    return render_template("quiz.html", country=country)


if __name__ == "__main__":
    app.run(debug=True)