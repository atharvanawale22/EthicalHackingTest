from flask import Flask, request, render_template_string
import csv
import random

app = Flask(__name__)

CSV_FILE = "ethical_hacking_mcqs_clean.csv"


def load_questions():
    questions = []
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not all([row.get('question'), row.get('option1'), row.get('option2'), row.get('option3'), row.get('option4'), row.get('answer')]):
                continue
            questions.append({
                "question": row['question'].strip(),
                "options": [row.get('option1', '').strip(),
                            row.get('option2', '').strip(),
                            row.get('option3', '').strip(),
                            row.get('option4', '').strip(),
                            row.get('option5', '').strip()],
                "answer": [ans.strip() for ans in row['answer'].split(";") if ans.strip()]
            })
    return random.sample(questions, min(50, len(questions)))


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ethical Hacking MCQ Test - Made by Atharva Nawale</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #e0f7fa; padding: 20px; }
        .container { max-width: 960px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #00695c; margin-bottom: 5px; }
        .subheading { text-align: center; font-style: italic; color: #444; margin-bottom: 25px; }
        .question-block { margin-bottom: 30px; padding: 20px; border-radius: 8px; border: 1px solid #ccc; background-color: #fdfdfd; }
        .correct { background-color: #d4edda; padding: 5px; border-radius: 5px; }
        .wrong { background-color: #f8d7da; padding: 5px; border-radius: 5px; }
        .normal { padding: 5px; border-radius: 5px; }
        .buttons { margin-top: 30px; text-align: center; }
        .summary { text-align: center; font-size: 18px; margin-top: 20px; color: #333; }
        button {
            padding: 12px 24px;
            margin: 10px;
            border: none;
            background-color: #007BFF;
            color: white;
            font-size: 16px;
            border-radius: 6px;
            cursor: pointer;
        }
        button:hover { background-color: #0056b3; }
    </style>
</head>
<body>
<div class="container">
    <h1>Ethical Hacking MCQ Test</h1>
    <div class="subheading">Made by Atharva Nawale</div>

    {% if questions %}
    <form method="POST">
        {% for q in questions %}
        {% set q_index = loop.index0 %}
        <div class="question-block">
            <p><strong>{{ loop.index }}. {{ q.question }}</strong></p>
            {% for opt in q.options %}
            {% if opt %}
            <label>
                <input type="checkbox" name="q{{ q_index }}" value="{{ opt }}"> {{ opt }}
            </label><br>
            {% endif %}
            {% endfor %}
            <input type="hidden" name="answer{{ q_index }}" value="{{ q.answer | join(';') }}">
            <input type="hidden" name="text{{ q_index }}" value="{{ q.question }}">
            <input type="hidden" name="options{{ q_index }}" value="{{ q.options | join('||') }}">
        </div>
        {% endfor %}
        <div class="buttons">
            <button type="submit">Submit</button>
            <a href="/"><button type="button">Refresh</button></a>
        </div>
    </form>

    {% elif results %}
    <h2>Your Score: {{ score }} / {{ total }}</h2>
    <div class="summary">
        Percentage: {{ ((score / total) * 100) | round(2) }}%
    </div>
    {% for r in results %}
    <div class="question-block">
        <p><strong>{{ loop.index }}. {{ r.question }}</strong></p>
        {% for opt in r.all_options %}
        {% if opt %}
        <div class="{% if opt in r.correct_answer and opt in r.user_answer %}correct{% elif opt in r.user_answer and opt not in r.correct_answer %}wrong{% elif opt in r.correct_answer %}correct{% else %}normal{% endif %}">
            {{ opt }}
        </div>
        {% endif %}
        {% endfor %}
    </div>
    {% endfor %}
    <div class="buttons">
        <a href="/"><button>Try Another Set</button></a>
    </div>
    {% endif %}
</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        total = 0
        score = 0
        results = []
        for i in range(50):
            selected = request.form.getlist(f'q{i}')
            answer_raw = request.form.get(f'answer{i}')
            question_text = request.form.get(f'text{i}')
            options_raw = request.form.get(f'options{i}')
            if not answer_raw or not options_raw:
                continue
            correct_answers = [a.strip() for a in answer_raw.split(";") if a.strip()]
            all_options = [opt.strip() for opt in options_raw.split("||") if opt.strip()]
            total += 1
            if sorted(selected) == sorted(correct_answers):
                score += 1
            results.append({
                "question": question_text,
                "all_options": all_options,
                "user_answer": selected,
                "correct_answer": correct_answers
            })
        return render_template_string(HTML_TEMPLATE, results=results, score=score, total=total)

    questions = load_questions()
    return render_template_string(HTML_TEMPLATE, questions=questions)


if __name__ == "__main__":
    app.run(debug=True)
