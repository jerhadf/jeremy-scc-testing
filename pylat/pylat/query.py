#from pylat.testrunner import get_config
#from pylat.configvalues import USE_QB
#from pylat.configvalues import QB_CLIENT
import pylat.cmdclient


def ask_question(question, answers, img=None):
    return pylat.cmdclient.post_question(question, answers, img)
    #if get_config(USE_QB):
    #    return get_config(QB_CLIENT).post_question(question, answers, img)
    #else:
    #    return pylat.cmdclient.post_question(question, answers, img)
