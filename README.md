# Real-time-monitor-system
### Author: Zhao-Shun Zheng, Cheng Han Yu  
### Date: 2021/6/19
### email: e14051148@gs.ncku.edu.tw, n26094304@gs.ncku.edu.tw
---
## Development environment
 *Development environment include MySQL, Python, Qt designer and Mosquitto*
 
![image](https://user-images.githubusercontent.com/48173999/122632344-d34c4f00-d104-11eb-98f9-74826821da5f.png)
## System Architecture
![image](https://user-images.githubusercontent.com/48173999/122633822-1f02f680-d10d-11eb-9b3b-6c4044288253.png)

#### PC1 run *Send folder*
#### PC3 run *Receive folder*
## Data 
We can get data from other groups.  
- Group 1 - *ID, Object name, Finish time and ID of Shipment* 
- Group 2 - *ID, Object name, position of object and webcam video* 
- Group 4 - *ID, Object name, class of object* 
- Group 5 - *ID, Object name, start time* 
- Group 6 - *ID, Object name, result of defect detection and image* 
## How to use
#### First Step
1. Open Mosquitto Broker and allow other PC to connect
2. Run Send/Socket_Pulisher.ipynb to wait for socket client for sending real time video
3. Run Send/MQTT_Pulisher.ipynb to send data to Broker
#### Senond Step
1. Run Receive/MQTT_Subscriber.ipynb to receive data and push data into DB
2. Run Receive/User Interface/main.py to open User interface for showing data and real time video
#### Note
Please modify Receive/MQTT_Subscriber.ipynb to connect correct address of DB before using programs. 
## User Interface
#### *First - Log in interface* 
![image](https://user-images.githubusercontent.com/48173999/122633850-4659c380-d10d-11eb-9744-a91b021927e9.png)
#### *Second - Main interface*
- Monitor - Real time WebCam video
- 時間查詢 - Serach data in your defined time from DB
- 工單 - Select data to show
- Query - Show data 
- 良率 - Perfect object / total object

![image](https://user-images.githubusercontent.com/86152478/122640808-f510fa80-d133-11eb-86b6-117bfda8062d.png)
#### *Third - Object Profile*
![image](https://user-images.githubusercontent.com/48173999/122634005-32fb2800-d10e-11eb-9313-54bdd00df604.png)

## File Explanation
- Send/Data - That means sensor data from other groups. If you want to run real data from sensor, you need to modify Send/MQTT_Pulisher.ipynb. *Note that Use JSON format.*
- Send/Image - That means image data from Group 6. If you want to run real image data from sensor, you need to modify Send/MQTT_Pulisher.ipynb. *Note that Use OpenCV tool.*
- Receive/Save Image - That means image sended from MQTT. 
- Receive/User Interface/Data - That means user information. If you want to add User, you need to modify *User Information.xls* and add the photo into *photo floder*.
- Receive/User Interface/Images - That means images used by Qt.
