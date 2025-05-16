

import torch.multiprocessing as mp
import logging
import webrtcvad
import pyaudio
import time
from faster_whisper import WhisperModel
import numpy as np
from tkinter import Tk
import tkgui


INT16_MAX_VALUE = 32768.0
SAMPLE_RATE = 16000
NO_CHANNELS = 1
BUFFER_SIZE = 128
format = '%(asctime)s: %(levelname)s: \
         %(processName)s : %(threadName)s:  %(funcName)s: %(message)s'




class audioTranscription:
    def __init__(self,q,q2):
        self.shutdown_event = mp.Event()
        self.is_working = mp.Event()
        self.is_working.set()
        self.q1 = q
        self.q2 = q2
        self.audio_process=None
        self.transcription_process=None

    def _process_start(self,targ=None,args=()):
        try:
            p = mp.Process(target=targ,args=args,daemon=True)
            return p
        except:
            logging.critical("Error in starting process %s",targ)
            raise

    def audio_recorder(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(rate=SAMPLE_RATE,channels=NO_CHANNELS,
                            format=pyaudio.paInt16,input=True)
            logging.info("PyAudio resource Inititalized")
            audio = bytearray()
            count=0
            try:
                while  self.is_working:
                    data = stream.read(BUFFER_SIZE)
                    audio.extend(data)
                    ##
                    count += 1
                    if count>=125:
                        self.q1.put(audio)
                        audio=bytearray()
                        count=0
                #self.q1.put(audio)
                logging.info("Shutdown Event set: No more recording")
            except Exception as e1:
                logging.exception("Error in recording job: %s",e1)
                
            finally:
                stream.close()
                p.terminate()
                logging.info("Audio Resource released")
        except Exception as e:
            logging.exception("Error audio resource initialization %s",e)
            
    
    def transcribe(self):
        try:
            model_t = WhisperModel('base.en',device='cpu',compute_type='int8')
            logging.info("Whisper model initialized")
            try:
                voice = bytearray()
                getFive = 5
                while  self.is_working:
                    if self.q1.qsize() > 5:
                        while getFive != 0:
                            x = self.q1.get()
                            voice.extend(x)
                            getFive -= 1
                        getFive = 5
                        try:
                            if len(voice) > 4:
                                v = np.frombuffer(voice,dtype=np.int16)
                                voice.clear()
                                v1 = v.astype(np.float32)/INT16_MAX_VALUE
                                seg,info = model_t.transcribe(v1)
                                strT = ''
                                for s in seg:
                                    print("[%.2fs -> %.2fs] %s" 
                                    % (s.start, s.end, s.text))
                                    strT.join(s.text)
                                self.q2.put(strT)
                                strT = ''
                        except Exception as e:
                            logging.exception("Error in transcription %s",e)
            except Exception as e:
                logging.exception("Error in transcribing %s",e)
                
                    
                    
        except Exception as e:
            logging.critical("Whisper model exception error %s",e)
        
        finally:
            while not self.q1.empty():
                z=self.q1.get()
            logging.info("Emptied Q")
        
    def start_process(self):
        self.audio_process = self._process_start(targ=self.audio_recorder)
        self.audio_process.start()
        logging.info("Audio Process Started ")
        self.transcription_process = self._process_start(targ=self.transcribe)
        self.transcription_process.start()
        logging.info("Transcription Process Started")

    def shutdown(self):
        self.shutdown_event.set()
        self.is_working.clear()
        logging.info("Set the Shutdown Event to set")
        print("Is audio_process alive",self.audio_process.is_alive())
        #if self.audio_process.is_alive(): self.audio_process.terminate()
        self.audio_process.join(1)
        print("is Transcript alive",self.transcription_process.is_alive())
        if self.transcription_process.is_alive() : self.transcription_process.terminate()
        self.transcription_process.join(1)
        print("both likely joined[timeout], ending... ")






if __name__ == '__main__' :
    mp.set_start_method('fork')
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='audioTrans.log',format=format,
                          filemode='w',level=logging.DEBUG)
    q=mp.Queue()
    q2=mp.Queue()
    a = audioTranscription(q,q2)
    root = Tk()
    b = tkgui.ViewTranscript(root,q2)
    try:
        a.start_process()
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()
    finally:
        a.shutdown()
    
    print("Out of Try Blocks Main ,Quit")
    
