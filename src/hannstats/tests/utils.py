
import unittest

from hannstats.utils import _get_candidates
from hannstats.utils import _get_snippet
from hannstats.utils import _clean_screenplay

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

    def test_candidates4(self):
        # Test season-3 style dialog
        snip = '\n                            HANNIBAL\n                  Bâtard-Montrachet and tartuffi\n                  bianchi.\n     PULL OUT to reveal he is --\n     INT. HANNIBAL LECTER\'S OFFICE - DAY\n\n     Hannibal sits behind his desk, across from ALANA BLOOM, the\n     gorgeous white truffle between them. There\'s a playful yet\n     slightly-challenging tone.\n                            ALANA BLOOM\n                  How I found you in Florence.\n                            HANNIBAL\n                  Betrayed by good taste. Is good\n                  taste itching at you in your daily\n                  rounds of institutional life?\n                            ALANA BLOOM\n                  An itch easy enough to scratch...\n     Alana takes a sip from her own glass of wine.\n                            ALANA BLOOM (CONT’D)\n                  ...when there\'s cause to celebrate.\n                      (off his look)\n                  Congratulations, Hannibal. You\'re\n                  officially insane.\n                             HANNIBAL\n                  There\'s no consensus in the\n                  psychiatric community what I should\n                  be termed.\n                            ALANA BLOOM\n                  You\'ve long been regarded by your\n                  peers in psychiatry as something\n                  entirely Other. For convenience,\n                  they term you a monster.\n\x0cHANNIBAL   Ep. #308 "The Great Red Dragon"   FINAL DRAFT   01/26/15   11.\n\n\n                            HANNIBAL\n                  What do you term me?\n\n                             ALANA BLOOM\n                  I don\'t.   You defy categorization.\n'
        expected = {"speaker": ["HANNIBAL", "ALANA BLOOM", "HANNIBAL", "ALANA BLOOM", "HANNIBAL", "ALANA BLOOM", "HANNIBAL", "ALANA BLOOM"],
                    "dialog": ["Bâtard-Montrachet and tartuffi bianchi.", 
                                "How I found you in Florence.", 
                                "Betrayed by good taste. Is good taste itching at you in your daily rounds of institutional life?", 
                                "An itch easy enough to scratch... ...when there\'s cause to celebrate. Congratulations, Hannibal. You\'re officially insane.", 
                                "There\'s no consensus in the psychiatric community what I should be termed.", 
                                "You\'ve long been regarded by your peers in psychiatry as something entirely Other. For convenience, they term you a monster.", 
                                "What do you term me?", 
                                "I don\'t.   You defy categorization."]
                    }

        result = _get_candidates(snip)

        self.maxDiff = None

        self.assertEqual(result, expected)

    def test_candidates5(self):
        # Test season3 style dialog

        # get the snippet
        sp_file = '/media/pball/T71/Peter/School/ENGL472/Assignment_2/hannstats/data/scripts/texts/H306-Dolce-121314.txt'
        with open(sp_file) as fp:
            sp = fp.read()

        snip = _get_snippet(sp, 174, 211)

        snip = _clean_screenplay(snip)
        print(snip)


        expected = {"speaker": ["WILL GRAHAM", "JACK CRAWFORD", "WILL GRAHAM", "JACK CRAWFORD", "WILL GRAHAM", "JACK CRAWFORD", "WILL GRAHAM", "JACK CRAWFORD", "WILL GRAHAM"],
                    "dialog":  ["Again.",
                                "We know how that usually turns out. Mason Verger is trying to capture Hannibal himself for purposes of personal revenge.",
                                "Have you told la polizia they're looking for Hannibal Lecter?",
                                "They're motivated to find Dr. Fell inside the law. Knowing who he is... and what he's worth, will just coax them out of bounds.",
                                "It would be a free-for-all.",
                                "And Hannibal would slip away. Would you slip away with him?",
                                "Part of me will always want to.",
                                "You have to cut that part out.",
                                "Of course you would find him here. Not because of the exhibit, but because of the crowd it attracts. You had him, Jack. He was beaten. Why didn't you kill him?"]}

        result = _get_candidates(snip)

        self.maxDiff = None

        self.assertEqual(result, expected)
