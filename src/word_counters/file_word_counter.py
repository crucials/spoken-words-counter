import wave
import time
import os
from typing import Literal

import pyaudio
from faster_whisper import WhisperModel

from word_counters import WordCounter


class FileWordCounter(WordCounter):
    def __init__(self,
                 audio_file_path: str,
                 language: str | None = None,
                 words_to_count: list[str] | None = None):
        super().__init__(language, words_to_count)
        
        self.audio_file_path = audio_file_path

    def start(self):
        print('started transcribing')

        segments_iterator, _ = WordCounter.speech_transcriber.transcribe(
            self.audio_file_path,
            language=self.language, 
            condition_on_previous_text=True
        )

        print('finished transcription')

        self._count_stats(' '.join([segment.text for segment in segments_iterator]))
