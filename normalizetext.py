import re
import inflect  # For number to words conversion

p = inflect.engine()

def normalize_text(text):
    """Applies common normalization steps to a text string."""
    text = text.lower()
    text = remove_punctuation(text)
    text = normalize_whitespace(text)
    # text = normalize_numbers(text)
    text = expand_contractions(text)
    return text

def remove_punctuation(text):
    """Removes punctuation from a string."""
    return re.sub(r'[^\w\s]', '', text)

def normalize_whitespace(text):
    """Removes leading/trailing whitespace and collapses multiple spaces."""
    return ' '.join(text.strip().split())

def normalize_numbers(text):
    """Converts numbers to their spoken word equivalents."""
    words = []
    for word in text.split():
        if word.isdigit():
            words.append(p.number_to_words(word))
        else:
            words.append(word)
    return ' '.join(words)

def expand_contractions(text):
    """Expands common English contractions."""
    contractions_map = {
        "ain't": "am not",
        "aren't": "are not",
        "can't": "cannot",
        "couldn't": "could not",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "hadn't": "had not",
        "hasn't": "has not",
        "haven't": "have not",
        "he'd": "he would",
        "he'll": "he will",
        "he's": "he is",
        "i'd": "I would",
        "i'll": "I will",
        "i'm": "I am",
        "i've": "I have",
        "isn't": "is not",
        "it'd": "it would",
        "it'll": "it will",
        "it's": "it is",
        "let's": "let us",
        "ma'am": "madam",
        "shan't": "shall not",
        "she'd": "she would",
        "she'll": "she will",
        "she's": "she is",
        "shouldn't": "should not",
        "that's": "that is",
        "there's": "there is",
        "they'd": "they would",
        "they'll": "they will",
        "they're": "they are",
        "they've": "they have",
        "wasn't": "was not",
        "we'd": "we would",
        "we'll": "we will",
        "we're": "we are",
        "we've": "we have",
        "weren't": "were not",
        "what'll": "what will",
        "what're": "what are",
        "what's": "what is",
        "what've": "what have",
        "where's": "where is",
        "who'd": "who would",
        "who'll": "who will",
        "who're": "who are",
        "who's": "who is",
        "who've": "who have",
        "won't": "will not",
        "wouldn't": "would not",
        "you'd": "you would",
        "you'll": "you will",
        "you're": "you are",
        "you've": "you have"
    }
    words = []
    for word in text.lower().split():
        if word in contractions_map:
            words.append(contractions_map[word])
        else:
            words.append(word)
    return ' '.join(words)