import regex
import pandas as pd
import numpy as np
import json
from itertools import combinations
from collections import defaultdict
from collections import Counter
import string

def _get_snippet(sp, start, end):
    # Given a screenplay and two line numbers,
    # Get the text between the line numbers
    lines = sp.split('\n')
    output = '\n'.join(lines[start-1:end-1])
    return output

def _clean_screenplay(sp):
    # Remove some garbage
    printable = set(string.printable)
    printable.remove(u'\x0c')
    sp = ''.join(filter(lambda x: x in printable, sp))
    sp = regex.sub(r"^[ ]*HANNIBAL (- PROD|Ep). #\d+.*$\n", "", sp, flags=regex.MULTILINE)
    return sp

def _get_candidates(screenplay):
    # First, remove interjected stage directions
    screenplay = regex.sub(r'^[ ]+\([\w .!?,’]+\)$\n', "", screenplay, flags=regex.MULTILINE)

    # Then, find chunks of text that look like dialog
    candidates = regex.findall(r'((?<=^[ ]{10,})[A-Z][A-Z .]+(\(CONT’D\))?$)\n(^([ ]{6,}.[^A-Z].+$\n)+)', # Get lines of dialog
                               screenplay,
                               flags=regex.MULTILINE)
    #print(len(candidates))
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
    
    screenplay = _clean_screenplay(screenplay)
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
    all_dialog = [dialog for dialog_list in [_get_character_dialog(char) for char in characters if len(char['names']) > 0] for dialog in dialog_list]

    # Sort all_dialog by index
    all_dialog = sorted(all_dialog, key=(lambda x: x[2]))

    # Make it a dataframe
    df = pd.DataFrame(all_dialog, columns=["speaker", "dialog", "index"])

    return df

def clean_AO3_text(text):
    # Given text from an AO3 story, clean up unwanted HTML content

    expr = regex.compile(r"<[^>]*>")
    cleaned = regex.sub(expr, "", text)

    return cleaned

def flip_mapping(mapping):
    # given a mapping of string to list of string, return an inverse mapping. Assumes that lists are mutually exclusive

    return {e: k for k, v in mapping.items() for e in v}

def load_texts(filepaths):
    texts = []
    for path in filepaths:
        with open(path) as fp:
            text = fp.read()
            texts.append(text)

    return texts

def tokens_to_network(tokens_path, book_path,  character_bins, dist=15):
    # Given the path to a .tokens and corresponding .book file produced by booknlp, return a dataframe with the social network for that graph
    # dist: upper limit for number of words between two characters to constitute a mention

    tok = pd.read_csv(tokens_path, sep='\t')
    with open(book_path) as fp:
        book = json.load(fp)['characters']
    char_ids = tok['characterId']
    char_ids = char_ids[~(char_ids == 'O')]
    char_ids = char_ids.map(lambda x: book[int(x)]['names'][0]['n'].lower() if x != '-1' else x)
    cbins = load_character_bins(character_bins)
    char_ids = char_ids.map(lambda x: cbins[x] if x in cbins else x.title())

    edges = defaultdict(Counter)


    # Slide a window over the character Ids
    for i in range(len(char_ids)-dist):
        window = char_ids[i:i+dist]

        characters = window.unique()
        characters = characters[characters != '-1']
        pairs = combinations(characters, 2)
        for pair in pairs:
            # Get character names
            name1 = pair[0]
            name2 = pair[1]
            # increase edge weight between the two characters by 1
            edges[name1][name2] += 1

    # Now just make the edges dict into a dataframe
    data = {"source": [], "target": [], "type": [], "weight": []}

    for char, edge in edges.items():
        for char2, weight in edge.items():
            data["source"].append(char)
            data["target"].append(char2)
            data["type"].append("undirected")
            data["weight"].append(weight)

    df = pd.DataFrame(data)
    return df

def _get_scenes(script):
    scenemarker_1 = regex.compile(r"^([AB]?\d+)[ ]*[A-Z .\-’,]+\1$", flags=regex.MULTILINE)
    scenemarker_2 = regex.compile(r"^[ ]*(?:INT.|EXT.)[A-Z .\-’,]+$", flags=regex.MULTILINE)
    if regex.search(scenemarker_1, script):
        scenes = regex.split(scenemarker_1, script)[0::2]
        #print("regex 1")
    elif regex.search(scenemarker_2, script):
        scenes = regex.split(scenemarker_2, script)
        #rint("regex 2")
    return scenes

def load_character_bins(cbin_path):
    # Load up the character_bins file and reverse the mapping
    with open(cbin_path) as fp:
        cbins = json.load(fp)

    cbins = flip_mapping(cbins)
    return cbins

def script_to_network(script, character_bins):
    # Given a Hannibal script as a string, make a graph frame based on characters who appear in the same scene as one another
    # Also include character_bins path for binning
    cbins = load_character_bins(character_bins)

    script = _clean_screenplay(script)
    #print(len(script))
    scenes = _get_scenes(script)

    scene_dialogs = [screenplay_to_dialog_table(s) for s in scenes]
    #print("boink", scenes[1])

    for scene in scene_dialogs:
        scene['speaker'] = scene['speaker'].map(lambda x: cbins[x.lower()] if x.lower() in cbins else x.title())

    edges = defaultdict(Counter)

    for scene in scene_dialogs:
        characters = scene['speaker'].unique()
        characters = sorted(characters)
        pairs = combinations(characters, 2)

        for pair in pairs:
            edges[pair[0]][pair[1]] += 1

    # Now just make the edges dict into a dataframe
    data = {"source": [], "target": [], "type": [], "weight": []}

    for char, edge in edges.items():
        for char2, weight in edge.items():
            data["source"].append(char)
            data["target"].append(char2)
            data["type"].append("undirected")
            data["weight"].append(weight)

    df = pd.DataFrame(data)
    return df

def fandom_network(fandom, character_bins):
    # Given the complete dict of a fandom, return the graph frame of characters co-occurring in stories together
    cbins = load_character_bins(character_bins)
    edges = defaultdict(Counter)

    for fic in fandom:
        characters = sorted(fic['characters'])
        characters = map(lambda x: cbins[x.lower()] if x.lower() in cbins else x, characters)
        pairs = combinations(characters, 2)

        for pair in pairs:
            edges[pair[0]][pair[1]] += 1

    # Now just make the edges dict into a dataframe
    data = {"source": [], "target": [], "type": [], "weight": []}

    for char, edge in edges.items():
        for char2, weight in edge.items():
            data["source"].append(char)
            data["target"].append(char2)
            data["type"].append("undirected")
            data["weight"].append(weight)

    df = pd.DataFrame(data)
    return df