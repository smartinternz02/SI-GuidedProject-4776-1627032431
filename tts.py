#Text to Speech Conversion
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import playsound

authenticator = IAMAuthenticator('90ZND2exsa6Qa96XDSMbt4zilsWbZzxP0CZMCUN3MVBD')
text_to_speech = TextToSpeechV1(
    authenticator=authenticator
)

text_to_speech.set_service_url('https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/29fa5bbf-695b-440b-a597-ff8b094a4abe')        
# here tts.wav is our file name and wb is write byte by byte in particular file as audio file as type it is python file handling procedure
with open('mall.mp3', 'wb') as audio_file:  #chaning wav to mp3
    audio_file.write(
        text_to_speech.synthesize(
            'Please wear mask to enter into Mall',
            voice='en-US_AllisonV3Voice',
            accept='audio/mp3'  #changing wav to mp3  
        ).get_result().content)
print('Playing..............')
playsound.playsound('mall.mp3')
print('stopped!')
#it is basically saving in folder but we have to play manually so to avoid this we are going to install playsound module
 
