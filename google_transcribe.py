import sounddevice as sd
import queue
import threading
import sys
from google.cloud import speech
import os
import csv
import evaltests as metric
import normalizetext as nn
import time
# --- Configuration ---
SAMPLE_RATE = 20000  # Sample rate in Hz (adjust based on mic and model)
CHUNK_SIZE = int(SAMPLE_RATE / 10) # 100ms chunks
LANGUAGE_CODE = "en-US" # Language to transcribe

# --- Global Queue to pass audio data ---
audio_queue = queue.Queue()
transcription_queue = queue.Queue()  # Queue to hold the transcribed text
# --- Sounddevice callback ---
def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # Add audio data to the queue
    audio_queue.put(bytes(indata))
def transcribe_audio(audio_file):
    """Transcribes audio from a local file using Google Cloud Speech-to-Text.

    Args:
        audio_file (str): Path to the local audio file.

    Returns:
        str: The transcribed text, or None if transcription fails.
    """
    try:
        client = speech.SpeechClient()

        with open(audio_file, "rb") as f:
            content = f.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            # sample_rate_hertz=20000,  # Adjust based on your audio file's sample rate
            language_code="en-US",    # Adjust to the language of your audio
        )

        response = client.recognize(config=config, audio=audio)

        transcription = ""
        for result in response.results:
            transcription += result.alternatives[0].transcript + " "
        return transcription.strip()

    except Exception as e:
        print(f"Error during transcription: {e}")
        return None
# --- Google Cloud transcription function ---
def google_transcribe_stream():
    """Handles sending audio to Google Cloud and printing results."""
    credential_path = "yorfilepath"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE, # translates to the more detailed representation of the audio signal/quality
        language_code=LANGUAGE_CODE,
        enable_automatic_punctuation=True
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True ,# Get partial results
       
    )

    # Generator function to yield audio chunks from the queue
    def audio_generator():
        while True:
            chunk = audio_queue.get()
            if chunk is None: # Signal to stop
                break
            yield speech.StreamingRecognizeRequest(audio_content=chunk)
            audio_queue.task_done() # Mark task as done after yielding

    print("Listening via Google Cloud... Press Ctrl+C to stop.")
    requests = audio_generator()
    responses = client.streaming_recognize(streaming_config, requests)

    try:
        for response in responses:
            if not response.results:
                continue
            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since final results are cumulative.
            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            if result.is_final:
                #print(f"Final:     {transcript}")
                transcription_queue.put((transcript, True))
            else:
                # Print interim results, overwriting the previous interim line
                #print(f"Interim:   {transcript}", end='\r')
                transcription_queue.put((None, True)) # Signal error
                # return transcript #yield transcript , False
        # return transcript

    except Exception as e:
        print(f"\nError during transcription: {e}")
        transcription_queue.put((None, True)) # Signal error
    finally:
        print("\nTranscription stopped.")
        # Signal the audio generator to stop if it hasn't already
        audio_queue.put(None)
        transcription_queue.put((None, True)) # Signal error
def start_google_transcription_thread():
    """Starts the Google Cloud transcription in a separate thread."""
    transcribe_thread = threading.Thread(target=google_transcribe_stream, daemon=True)
    transcribe_thread.start()
    return transcribe_thread

# --- Main execution ---
if __name__ == "__main__":
    reference_sentences=[]
    medium="stream"
    with open('transcriptionsoriginal.csv', 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        for  row in reader:            
            # Process your row data            
            reference_sentences.append(nn.normalize_text(', '.join(row)))
            
    audio_files = [] # List to store paths to your audio files
    # Start Google Cloud transcription in a separate thread
    
    transcribe_thread = start_google_transcription_thread()

    # Start recording audio
    try:
        if medium== "stream":
            print(f"stream")
            with sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=CHUNK_SIZE,
                device=None, # Default input device
                dtype='int16', # LINEAR16 encoding expects 16-bit signed integers
                channels=1, # Mono audio
                callback=audio_callback
            ):
                # Keep the main thread alive until Ctrl+C
                while True:
                    while not transcription_queue.empty():
                        transcript, is_final = transcription_queue.get_nowait()
                        if transcript:
                            # Process the transcribed text here
                            if is_final:
                                print(f"Main Thread (Final): {transcript}")
                                overall_wer = metric.calculate_wer("What is the very latest breaking news update regarding the international stock market today?", transcript)
                                print(f"Word Error Rate (WER): {overall_wer}")
                            else:
                                pass#print(f"Main Thread (Interim): {transcript}")
                        elif is_final is True: # Check for the end signal
                            print("Transcription finished.")
                            break

                    time.sleep(0.1)
        else:
            for i in range(1, 101):
                audio_files.append(f"mono_{i}.wav")

            transcriptions = []
            for i, audio_file in enumerate(audio_files):
                print(f"Transcribing: {audio_file}")
                transcriptions.append(nn.normalize_text(transcribe_audio(audio_file)))
                print(f"Transcribing: store in hash table {reference_sentences[i]}")
                #transcriptions[i] = transcription
                print(f"Original: {reference_sentences[i]}")
                print(f"Transcription: {transcriptions[i]}\n")        
           
            # reference_sentences=reference_sentences
            hypothesis_sentences = transcriptions 
            print(reference_sentences[24])
            print(hypothesis_sentences[24])
            if len(reference_sentences) != len(hypothesis_sentences):
                print("Error: The number of reference and hypothesis sentences must be the same.")
            else:
                overall_wer = metric.calculate_wer(reference_sentences, hypothesis_sentences)
                overall_cer = metric.calculate_cer(reference_sentences, hypothesis_sentences)
                overall_bleu = metric.calculate_overall_bleu(reference_sentences, hypothesis_sentences)
                hallucination_threshold = 0.6
                potential_hallucinations = metric.check_overall_hallucinations(reference_sentences, hypothesis_sentences, hallucination_threshold)

                print("--- Overall Evaluation Metrics ---")
                print(f"Overall Word Error Rate (WER): {overall_wer:.4f}")
                print(f"Overall Character Error Rate (CER): {overall_cer:.4f}")
                print(f"Overall BLEU Score: {overall_bleu:.4f}")
                print(f"Potential for Overall Hallucinations (Threshold={hallucination_threshold}): {potential_hallucinations}")



    except KeyboardInterrupt:
        print("\nStopping recording...")
        # Signal the transcription thread to finish by putting None in the queue
        audio_queue.put(None)
        # Wait for the transcription thread to finish cleanly
        transcribe_thread.join()
    except Exception as e:
        print(f"An error occurred: {e}")

    print("Program finished.")