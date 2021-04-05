import regex
import pandas as pd

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


    
