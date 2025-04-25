from jiwer import wer, cer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def calculate_wer(references, hypotheses):
    """Calculates the overall Word Error Rate (WER) for a list of sentences."""
    return wer(references, hypotheses)

def calculate_cer(references, hypotheses):
    """Calculates the overall Character Error Rate (CER) for a list of sentences."""
    return cer(references, hypotheses)

def calculate_overall_bleu(references, hypotheses):
    """Calculates the overall BLEU score for a list of sentence pairs.
    This is a simplified approach by averaging sentence-level BLEU scores.
    More sophisticated methods might consider corpus-level BLEU.
    """
    total_bleu = 0
    smoothing_function = SmoothingFunction().method1
    for ref, hyp in zip(references, hypotheses):
        total_bleu += sentence_bleu([ref.split()], hyp.split(), smoothing_function=smoothing_function)
    return total_bleu / len(references) if references else 0

def check_overall_hallucinations(references, hypotheses, threshold=0.6):
    """A basic heuristic to check for potential overall hallucinations
    by looking at the average BLEU score.

    Args:
        references: A list of ground truth sentences.
        hypotheses: A list of generated or transcribed sentences.
        threshold: A threshold (0 to 1) below which the average BLEU
                   score might indicate a higher likelihood of hallucinations.

    Returns:
        True if potential overall hallucination is suggested, False otherwise.
    """
    avg_bleu = calculate_overall_bleu(references, hypotheses)
    return avg_bleu < threshold


    # You can also iterate through each sentence pair for individual analysis if needed
    """
    print("\n--- Per Sentence Analysis ---")
    for i in range(len(reference_sentences)):
        ref = reference_sentences[i]
        hyp = hypothesis_sentences[i]
        sentence_wer = calculate_wer(ref, hyp)
        sentence_cer = calculate_cer(ref, hyp)
        sentence_bleu = calculate_bleu(ref, hyp)
        sentence_hallucination = check_hallucinations(ref, hyp, hallucination_threshold)
        print(f"Sentence {i+1}:")
        print(f"  Reference: {ref}")
        print(f"  Hypothesis: {hyp}")
        print(f"  WER: {sentence_wer:.4f}")
        print(f"  CER: {sentence_cer:.4f}")
        print(f"  BLEU: {sentence_bleu:.4f}")
        print(f"  Potential Hallucination: {sentence_hallucination}")
    """