# import unittest
# import os

# from qbclient import QbClient

# import pylat
# from pylat.configvalues import QB_CHANNEL
# from pylat.configvalues import SESSION_ID
# from pylat.configvalues import QB_CLIENT


# class SetupQB(unittest.TestCase):

#     def test_addConfig(self):
#         user = os.getenv('QB_USER', False)
#         password = os.getenv('QB_PASS', False)
#         self.assertTrue(user, "Unable to find env variable QB_USER")
#         self.assertTrue(password, "Unable to find env variable QB_PASS")
#         qb = QbClient(user, password)
#         self.assertTrue(qb.start_session(pylat.get_config(SESSION_ID), pylat.get_config(QB_CHANNEL)))
#         pylat.set_config(QB_CLIENT, qb)
