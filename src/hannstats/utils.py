import regex
import pandas as pd
import json

def _get_candidates(screenplay):
    CHAR_NAME_SPACES = 26
    DIALOG_SPACES = 15

    # First, remove interjected stage directions
    screenplay = regex.sub(r'^[ ]+\([\w .!?,’]+\)$\n', "", screenplay, flags=regex.MULTILINE)

    # Then, find chunks of text that look like dialog
    candidates = regex.findall(r'((?<=^[ ]{10,})[A-Z][A-Z ]+(\(CONT’D\))?$)\n(^([ ]{5,}\w[\w .!?,’“”]+$\n)+)', # Get lines of dialog
                               screenplay,
                               flags=regex.MULTILINE)

    # Extract speaker and dialog
    speaker = [cand[0] for cand in candidates]
    dialog = [cand[2] for cand in candidates]

    # Clean dialog
    dialog = [regex.sub(r'^[ ]+', "", d, flags=regex.MULTILINE) for d in dialog]
    dialog = [regex.sub(r'\n(?!$)', " ", d) for d in dialog]
    dialog = [d.strip('\n') for d in dialog]

    speaker_merged = []
    dialog_merged = []
    i = 0
    while i < len(speaker):
        j = 1
        full_dialog = dialog[i]

        # Gather continued dialog instances into one string
        while (i+j < len(speaker)) and (speaker[i+j] == speaker[i] + ' (CONT’D)'):
            full_dialog = full_dialog + ' ' + dialog[i+j]
            j += 1
        
        speaker_merged.append(speaker[i])
        dialog_merged.append(full_dialog)
        i += j


    #Format as dict
    data = {"speaker": speaker_merged, "dialog": dialog_merged}
    return data


def screenplay_to_dialog_table(screenplay):
    '''
    Take a Hannibal script as a string input, extract and format all dialogue instances.

    screenplay: string; works best on direct pdf-to-text output
    '''
    

    data = _get_candidates(screenplay)

    df = pd.DataFrame(data)

    return df

def _get_character_dialog(character):
    # Given a dict from the 'characters' list of a booknlp .book file, return all dialog as list of tuples of form
    # (character_name, line_of_dialog, index_of_line)

    name = character['names'][0]['n']
    dialog = []
    for line in character['speaking']:
        dialog.append((name, line['w'], line['i']))

    return dialog

    
def load_bnlp_dialog(book_path):
    '''
    Given the path to a .book file produced by booknlp, return a pandas dataframe with
    ordered dialog instances and their speakers.

    book_path: path to the .book file
    '''

    with open(book_path) as fp:
        book = json.load(fp)

    characters = book['characters']

    # Get one big list of all dialog
    all_dialog = [dialog for dialog_list in [_get_character_dialog(char) for char in characters] for dialog in dialog_list]

    # Sort all_dialog by index
    all_dialog = sorted(all_dialog, key=(lambda x: x[2]))

    # Make it a dataframe
    df = pd.DataFrame(all_dialog, columns=["speaker", "dialog", "index"])

    return df


