
import unittest

from hannstats.utils import _get_candidates

class UtilsTestCase(unittest.TestCase):

    def test_candidates1(self):
        # Test a basic case
        snip = '                           WILL GRAHAM\n                 I feel like I’m dreaming.\n\n                           JACK CRAWFORD\n                 The head was reported stolen last\n                 night about a mile from here.\n\n                           WILL GRAHAM\n                 Just the head?\n                 I also say this.\n                 And this!!\n\n     Brian Zeller, Beverly Katz, and Jimmy Price are combing the\n     immediate area for forensic evidence. Jack and Will stare as\n     Beverly and Brian Zeller attempt to shoo the crows away.\n\n                           JACK CRAWFORD\n                 Minneapolis homicide has already\n                 made a statement. They’re calling\n                 him the “Minnesota Shrike.”\n\n'
        expected = {"speaker": ['WILL GRAHAM', 'JACK CRAWFORD', 'WILL GRAHAM', 'JACK CRAWFORD'],
                    "dialog":  ["I feel like I’m dreaming.", "The head was reported stolen last night about a mile from here.", "Just the head? I also say this. And this!!", "Minneapolis homicide has already made a statement. They’re calling him the “Minnesota Shrike.”"]}

        result = _get_candidates(snip)

        self.assertEqual(result, expected)

    def test_candidates2(self):
        # Test stage-direction removal
        snip = '     A CHYRON tells us we are --\n\n     BLOOMINGTON, MINNESOTA\n\n                         ABIGAIL\n               Hello? Just a second.\n                   (to her father)\n               Dad. It’s for you.\n\x0c      HANNIBAL - PROD. #101 - DBL GREEN Collated   6/26/13         43.\n\n\n                            JACOB\n               Who is it?\n\n                         ABIGAIL\n               Caller i.d. said it was work.\n\n     She hands Jacob the phone and he presses it to his ear.\n\n'
        expected = {"speaker": ['ABIGAIL', 'JACOB', 'ABIGAIL'],
                    "dialog":  ["Hello? Just a second. Dad. It’s for you.", "Who is it?", "Caller i.d. said it was work."]}

        result = _get_candidates(snip)

        self.assertEqual(result, expected)

    def test_candidates3(self):
        # Test continued dialog mentions
        snip = '                            JACK CRAWFORD\n                  What are you doing in here?\n\n                            WILL GRAHAM\n                  I enjoy the smell of urinal cake.\n\n                             JACK CRAWFORD\n                  Me, too.   Lets talk.\n\n     An AGENT ENTERS to use the facilities.     Jack holds the door.\n\n                            JACK CRAWFORD (CONT’D)\n                  Use the ladies room.\n\n     The Agent abruptly turns and EXITS. Will eyes Jack closing\n     the door, realizing he’s not getting by without conversation.\n\n                            JACK CRAWFORD (CONT’D)\n                  Do you respect my judgement, Will?\n\n                             WILL GRAHAM\n                  Yes.\n\n'
        expected = {"speaker": ['JACK CRAWFORD', 'WILL GRAHAM', 'JACK CRAWFORD', 'WILL GRAHAM'],
                    "dialog": ["What are you doing in here?", "I enjoy the smell of urinal cake.", "Me, too.   Lets talk. Use the ladies room. Do you respect my judgement, Will?", "Yes."]}

        result = _get_candidates(snip)

        self.assertEqual(result, expected)