import sounddevice as sd
import os
import time
import azure.cognitiveservices.speech as speechsdk
import threading
import logging
import csv
import evaltests as metric
import normalizetext as nn
# --- Configuration ---
SAMPLE_RATE = 20000
CHUNK_SIZE = int(SAMPLE_RATE / 10) # Not directly used by Azure SDK like this, but good for understanding
LANGUAGE_CODE = "en-US"


speech_config = speechsdk.SpeechConfig(subscription="yourkey", region="yourregion")
speech_config.AudioSampleRate = 16000

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# --- Synchronization ---
done = threading.Event() # Use an event to signal completion

# --- Event Handlers ---
def recognized_handler(evt):
    print(evt.result.text)
    print(f"{evt.result.text}")    
    overall_wer = metric.calculate_wer("What is the very latest breaking news update regarding the international stock market today?", evt.result.text)
    print(f"Overall Word Error Rate (WER): {overall_wer:.4f}")
    # Example: Stop if the user says "stop listening"
    if "stop listening." in evt.result.text.lower():
        print("Stop keyword detected. Stopping recognition...")
        speech_recognizer.stop_continuous_recognition_async()
        done.set() # Signal the main thread - typically done in session_stopped
def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
    """Callback for intermediate recognition results."""
    print(f'Interim:   {evt.result.text}', end='\r')
def session_stopped_handler(evt):
    print(f"SESSION STOPPED: {evt}")
    done.set() # Signal the main thread that the session has ended

def canceled_handler(evt):
    # --- !! THIS IS THE KEY HANDLER TO CHECK !! ---
    print(f"CANCELED: Reason - {evt.reason}") # Tells you *why* it stopped
    if evt.reason == speechsdk.CancellationReason.Error:
        print(f"CANCELED: ErrorCode - {evt.error_code}") # Specific error code
        print(f"CANCELED: ErrorDetails - {evt.error_details}") # Detailed message from service
        print("CANCELED: Did you update the subscription info?")
    done.set() # Signal main thread to exit
def transcribe_audio(audio_file):
    audio_input = speechsdk.AudioConfig(filename=audio_file)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    result = speech_recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "No speech could be recognized"
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
       
        return f"Speech Recognition canceled: {cancellation_details.reason}"

def azure_transcribe_stream():
    # Connect handlers
    speech_recognizer.recognized.connect(recognized_handler)    
    speech_recognizer.session_stopped.connect(session_stopped_handler)
    speech_recognizer.canceled.connect(canceled_handler)
    # --- Start Recognition ---
    speech_recognizer.start_continuous_recognition_async()
    print("Speech recognition started. Speak into your microphone...")
    # --- Keep the Main Thread Alive using the Event ---
    # Blocks here until done.set() is called from an event handler
    done.wait() 
    speech_recognizer.stop_continuous_recognition_async()
    

# --- Main Execution ---
if __name__ == "__main__":
    # Run Azure transcription in the main thread or a separate one if needed
    # For this SDK, running in main thread and using events is often simplest
    reference_sentences=[]
    medium="stream"
    with open('transcriptionsoriginal.csv', 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        for  row in reader:            
            # Process your row data            
            reference_sentences.append(nn.normalize_text(', '.join(row)))
            
    audio_files = [] # List to store paths to your audio files
    try:
        print("First")
        if medium=="stream":
            azure_transcribe_stream()
        else:
        
            for i in range(1, 26):
                audio_files.append(f"mono_{i}.wav")

            transcriptions = []
            for i, audio_file in enumerate(audio_files):
                print(f"Transcribing: {audio_file}")
                transcriptions.append(nn.normalize_text(transcribe_audio(audio_file)))
                print(f"Transcribing: store in hash table {reference_sentences[i]}")
                #transcriptions[i] = transcription
                print(f"Original: {reference_sentences[i]}")
                print(f"Transcription: {transcriptions[i]}\n")        
           
        reference_sentences=reference_sentences[0:25] 
        hypothesis_sentences = transcriptions[0:25]  
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
        print("\nCtrl+C detected. Signaling stop...")
        done.set() # Signal the Azure loop to stop cleanly
    except Exception as e:
        print(f"An error occurred: {e}")
        done.set() # Also signal stop on other errors
    print("Program finished.")