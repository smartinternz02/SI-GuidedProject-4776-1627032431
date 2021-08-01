import numpy as np
import cv2
import random
import datetime
import playsound
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from ibmcloudant.cloudant_v1 import CloudantV1
from ibmcloudant import CouchDbSessionAuthenticator
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator


# Constants for IBM COS values
COS_ENDPOINT = "https://s3.jp-tok.cloud-object-storage.appdomain.cloud" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "Lr-m_jKYrbHuRcDO45dnBEd-H26jHD6Wmh7FAtn4LqEP" # eg "W00YixxxxxxxxxxMB-odB-2ySfTrFBIQQWanc--P3byk"
COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/dcc788127208455985d15643f9678c56:4df662aa-3049-41f5-8336-2fe25f96d5cc::"

# Create resource
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

#cloudant db
authenticator = BasicAuthenticator('apikey-v2-1c8tm43fw1elxdwju8zovlvu6g2n31ui2jxlq9sd4meb', 'acade081f4e9525c211c3be60c4f0fa8')
service = CloudantV1(authenticator=authenticator)
service.set_service_url('https://apikey-v2-1c8tm43fw1elxdwju8zovlvu6g2n31ui2jxlq9sd4meb:acade081f4e9525c211c3be60c4f0fa8@174d6264-82a3-42e3-8266-24927df49f3f-bluemix.cloudantnosqldb.appdomain.cloud')

bucket = "naveenvits"
def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))


# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
mouth_cascade = cv2.CascadeClassifier('haarcascade_mcs_mouth.xml')
upper_body = cv2.CascadeClassifier('haarcascade_upperbody.xml')



# Adjust threshold value in range 80 to 105 based on your light.
bw_threshold = 80

# User message
font = cv2.FONT_HERSHEY_SIMPLEX
org = (30, 30)
weared_mask_font_color = (255, 255, 255)
not_weared_mask_font_color = (0, 0, 255)
thickness = 2
font_scale = 1
weared_mask = "Thank You for wearing MASK"
not_weared_mask = "You are restrictied to enter into Mall Please wear the MASK "

# Read video
cap = cv2.VideoCapture(0)

while 1:
    # Get individual frame
    ret, img = cap.read()
    img=cv2.resize(img,(1000,600))

    # Convert Image into gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Convert image in black and white
    (thresh, black_and_white) = cv2.threshold(gray, bw_threshold, 255, cv2.THRESH_BINARY)
    #cv2.imshow('black_and_white', black_and_white)

    # detect face
    faces=face_cascade.detectMultiScale(gray,1.1,4)

    # Face prediction for black and white
    faces_bw = face_cascade.detectMultiScale(black_and_white, 1.1, 4)


    if(len(faces) == 0 and len(faces_bw) == 0):
        cv2.putText(img, "No face found...", org, font, font_scale, weared_mask_font_color, thickness, cv2.LINE_AA)
    elif(len(faces) == 0 and len(faces_bw) == 1):
        # It has been observed that for white mask covering mouth, with gray image face prediction is not happening
        cv2.putText(img, weared_mask, org, font, font_scale, weared_mask_font_color, thickness, cv2.LINE_AA)
    else:
        # Draw rectangle on gace
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]


            # Detect lips counters
            mouth_rects = mouth_cascade.detectMultiScale(gray, 1.5, 5)

        # Face detected but Lips not detected which means person is wearing mask
        if(len(mouth_rects) == 0):
            cv2.putText(img, weared_mask, org, font, font_scale, weared_mask_font_color, thickness, cv2.LINE_AA)
        else:
            for (mx, my, mw, mh) in mouth_rects:

                if(y < my < y + h):
                    # Face and Lips are detected but lips coordinates are within face cordinates which `means lips prediction is true and
                    # person is not waring mask
                    cv2.putText(img, not_weared_mask, org, font, font_scale, not_weared_mask_font_color, thickness, cv2.LINE_AA)
                    # here tts.wav is our file name and wb is write byte by byte in particular file as audio file as type it is python file handling procedure
                    picname=datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
                    cv2.imwrite(picname+".jpg",img)
                    multi_part_upload(bucket, picname+'.jpg', picname+'.jpg')
                    json_document={"link":COS_ENDPOINT+'/'+bucket+'/'+picname+'.jpg'}
                    response = service.post_document(db='mask-detection', document=json_document).get_result()
                    print('Playing..............')
                    playsound.playsound('mall.mp3')
                    print('stopped!')
                    #cv2.rectangle(img, (mx, my), (mx + mh, my + mw), (0, 0, 255), 3)
                    break

    # Show frame with results
    cv2.imshow('Mask Detection', img)
    k = cv2.waitKey(30) & 0xff
    #press escape button 
    if k == 27:
        break

# Release video
cap.release()
cv2.destroyAllWindows()
