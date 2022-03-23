import cv2
import numpy as np
import time
import paho.mqtt.client as mqtt
import json

NETPIE_HOST = "mqtt.netpie.io"
CLIENT_ID = "f6ba6c10-1556-4bb9-b976-4c585be7800c"
DEVICE_TOKEN = "CbyZtkvmGjuSHfMWkMgTwjoSY64X2mMs"

data_status = {'status': 0}

def on_connect(client, userdata, flags, rc):
    print ("Result from connect: {}".format(
        mqtt.connack_string(rc)))
    client.subscribe("@shadow/data/updated")
    
client = mqtt.Client(protocol=mqtt.MQTTv311,
                     client_id=CLIENT_ID, clean_session=True)
client.username_pw_set(DEVICE_TOKEN)
client.on_connect = on_connect
client.connect(NETPIE_HOST , 1883)
client.loop_start()

try:
    webcam = cv2.VideoCapture(0)


    while(1):
        _, imageFrame = webcam.read()
    
        hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)
    
        sensitivity = 15
        lower = np.array([0,0,255-sensitivity])
        upper = np.array([255,sensitivity,255])

        mask = cv2.inRange(hsvFrame, lower, upper)
    
        kernal = np.ones((5, 5), "uint8")
    
        mask = cv2.dilate(mask, kernal)
        res = cv2.bitwise_and(imageFrame, imageFrame, 
                                  mask = mask)
    
        contours, hierarchy = cv2.findContours(mask,
                                               cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
    
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if(area > 300):
                x, y, w, h = cv2.boundingRect(contour)
                imageFrame = cv2.rectangle(imageFrame, (x, y), 
                                           (x + w, y + h), 
                                           (0, 0, 255), 2)
              
                cv2.putText(imageFrame, "On", (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                            (0, 0, 255), print("On" ,":" , time.strftime("%a, %d %b %Y %H:%M:%S")))
                data_status['status'] = "On" , time.strftime("%a, %d %b %Y %H:%M:%S")
                print(json.dumps({ "data" : data_status}))
                client.publish('@shadow/data/update', json.dumps({"data" : data_status }), 1)
                time.sleep(5)
            else:
                data_status['status'] = "Off" , time.strftime("%a, %d %b %Y %H:%M:%S")
                print(json.dumps({ "data" : data_status}))
                client.publish('@shadow/data/update', json.dumps({"data" : data_status }), 1)
                time.sleep(5)
                
                
                
        cv2.imshow("Multiple Color Detection in Real-TIme", imageFrame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break
except KeyboardInterrupt:
    pass
client.loop_start()
client.disconnect()