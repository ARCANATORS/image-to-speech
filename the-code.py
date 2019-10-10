# Dependencies are imported here.
# Check out ---->  https://cloud.google.com/python/docs/ for instruction to install the G-cloud dependencies.
import RPi.GPIO as GPIO
import time,os,pygame,datetime
from picamera import PiCamera
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import texttospeech

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/pi/Desktop/Arcanators-Pune-2e79d44dd7ac.json'


client = vision.ImageAnnotatorClient()
camera = PiCamera()


camera.resolution = (1080,720)



GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(18,GPIO.IN,pull_up_down=GPIO.PUD_UP)

#Initialize the pygame module for playing the audio files.
pygame.init()    #---> Uncomment this line in case there is problem with the sound playing part.
pygame.mixer.init()

print("Press Start button to read out the page")

# flag ---> Status flag to indicate the current status of audio file i.e. Playing/Paused.
# light_on ---> Status flag to check the current status of the LEDs i.e. ON/OFF.
flag=0
#light_on=0
file_playing=0

# Helper function to perform Text-to-Speech conversion using Google Text to SPeech API.
# text ---> The text to be converted to audio.
# audioname ---> The name of the output audio file.
def synthesize_text(text,audioname):
    
    # client ---> Initialised to TextToSpeech API Class.
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.types.SynthesisInput(text=text)
    
    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)
    
    # audion_config = configuration for the output audio file. Supports other formats such as WAV, AVI etc.
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)
   
    # response ---> Receives API response for the input text.
    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is in binary format. The audio content is written into the output file.
    with open(audioname, 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file {}'.format(audioname))

# Detect Capture button state.
# Capture new image if the camera capture button is pressed.
while True: 
    try:

        # capture_button ---> Button input to capture new image.
        # pause_button ---> Button input to pause/play audio file.
        capture_button = GPIO.input(16)
        #print(capture_button)
        pause_button = GPIO.input(18)
        #capture_button=0 #---> when it is pressed.
        
        if capture_button==False:
            print("button pressed")#---------------------------------- changed 
            time.sleep(0.2)
            flag=0
            print('Capturing new image...')

            # image_name ---> name of the captured image.
            image_name = "Book-"+datetime.datetime.now().strftime("%H-%M-%S")+".jpg"

            # 2 second sleep to give sufficient time for the camera to initialize.
            camera.start_preview()
            time.sleep(10)
            camera.capture(image_name)
            print("Image clicked . . .")
            camera.stop_preview()
           # image_name = cv2.cvtColor(image_name, cv2.COLOR_BGR2GRAY)
            # content ---> Image contents in binary.
            with open(image_name, 'rb') as image_file:
                content = image_file.read()
            print("Sending Image to OCR . . ")
            
            # Send the binary to OCR API for text extraction.
            image = types.Image(content=content)
            print(" st1 ---- exe ")
            response = client.document_text_detection(image=image)
            print(" st2 ---- exe ")
            labels = response.full_text_annotation
            print(" st3 ---- exe ")

            # Capitalize every word's first letter.
            # Add an additional identifier at the end, to signify end of file.
            s=""
            for i in labels.text.split():
                s+=i+" "
                t=""
                for i in s.split():
                    temp=i[0].upper()
                    temp2=i[1:].lower()
                    t+=temp+temp2+" "
            
            print("\n"+t)
            t+=". ,End Of Page"
            print("CONVERTING")

              # audioname ---> stores the name of the audio file.
            audioname="Book-"+datetime.datetime.now().strftime("%H-%M-%S")+".mp3"
            synthesize_text(t,audioname)
            print("Starting audio. . .")
            print("Press pause button to Pause/Resume")
            
            # Initialize the mixer to start playing the audio file.
            pygame.mixer.music.load(audioname)
            pygame.mixer.music.play()
            time.sleep(4)
            file_playing=1
            #os.system("vlc {}".format(audioname))

        # Check for pause button condition.
        # flag=0 ---> audio playing.
        # flag=1 ---> audio paused.
        if (pause_button == False):
            time.sleep(1)
            if flag==0: 
                pygame.mixer.music.pause()
                flag=1
                print("Paused. . . ")
            elif flag==1:
                pygame.mixer.music.unpause()
                flag=0
                print("Resumed. . . ")

                 
    except Exception as e:
        print("?sdsd")
        GPIO.cleanup()
        break
