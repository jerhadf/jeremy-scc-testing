
def post_question(question, answers, img=None):
    response = display_question(question, answers, img)
    while response not in answers:
        response = get_exact_response(answers)
    return response


def get_exact_response(answers):
    print("Invalid answer. Please use exact value {}: ".format(answers), end="", flush=True)
    return input()


def display_question(question, answers, img=None):
    print("{} {}: ".format(question, answers), end="", flush=True)
    return input()
