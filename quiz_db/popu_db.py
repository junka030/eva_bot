from app import app, db, Question, Choice

with app.app_context():
    questions = [
        {
            "question" : "Who is the pilot of EVA-00?",
            "choices" : [
                {"text" : "Ayanami Rei", "is_correct" : True},
                {"text" : "Ikari Shinji", "is_correct" : False},
                {"text" : "Soryu Asuka", "is_correct" : False},
                {"text" : "Nagisa Kaworu", "is_correct" : False}
            ]
        },
        {
            "question" : "Who is the pilot of EVA-02?",
            "choices" : [
                {"text" : "Ayanami Rei", "is_correct" : False},
                {"text" : "Ikari Shinji", "is_correct" : False},
                {"text" : "Soryu Asuka", "is_correct" : True},
                {"text" : "Nagisa Kaworu", "is_correct" : False}
            ]
        }
    ]

    for q in questions:
        question = Question(question=q['question'])
        db.session.add(question)
        db.session.commit()
        for c in q['choices']:
            choice = Choice(
                question_id=question.id,
                choice_text=c['text'],
                is_correct=c['is_correct']
            )
            db.session.add(choice)
            if c['is_correct']:
                question.answer_id = choice.id

        db.session.commit()