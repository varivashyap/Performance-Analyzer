import cv2
from ultralytics import YOLO
import pandas as pd



def detect_events(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    model = YOLO("/home/urvashi2022/Desktop/UI_DEVELOPMENT/DetectionMoreEvents/runs/detect/train10/weights/best.pt")
    frames_to_skip = 20
    frame_num = 0

    df = pd.DataFrame(columns=['Current time', 'Frame number', 'Event type', 'Confidence'])


    class_names = ['ball', 'Corner-kick', 'Free-kick', 'goalkeeper', 'player', 'Red-card', 'Referee', 'Shooting', 'Substitution', 'Yellow-card']
    while cap.isOpened():
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        current_time = frame_num // fps # in seconds
        if frame_num % 1000 == 0:
            print("Current time: ", current_time)
            print("Frame number: ", frame_num)  
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        if frame_num % frames_to_skip == 0:
            results = model(frame)
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    confidence = box.conf[0].cpu().item()
                    class_id = int(box.cls[0].cpu().item())
                    if class_id in [1, 2, 5, 7, 8, 9]:
                        print(f"Current time: {current_time}, Frame: {frame_num}, Class: {class_names[class_id]}, Confidence: {confidence}")
                        # add these details to the csv file
                        # Create a new DataFrame from the dictionary to be appended
                        new_row = pd.DataFrame([{'Current time': current_time, 
                                                'Frame number': frame_num, 
                                                'Event type': class_names[class_id], 
                                                'Confidence': confidence}])

                        # Concatenate the new row to the existing DataFrame
                        df = pd.concat([df, new_row], ignore_index=True)
        frame_num += 10

                    

    df = df.drop_duplicates(subset=['Current time'])
    # reindex the dataframe
    df = df.reset_index(drop=True)
    #convert time from seconds to minutes and seconds
    df['Current time'] = df['Current time'].apply(lambda x: f"{int(x//60)}:{int(x%60)}")
    df

    print(df)


    # count the number of times each event type occurs
    event_counts = df['Event type'].value_counts()
    event_counts

    Cols = ['Action', 'Corner-kick', 'Free-kick', 'Red-card', 'Shooting', 'Substitution', 'Yellow-card']



    event_type_counts = pd.DataFrame(columns=Cols)
    event_type_counts['Action'] = ['Count of Action']
    event_type_counts = event_type_counts.fillna(0)
    event_type_counts

    # count the number of times each event type occurs for each class in the class_names list
    for class_name in Cols:
        if class_name != 'Action':
            # find the number if types the event the class_name occurs
            event_counts = df[df['Event type'] == class_name]['Event type'].value_counts()
            # store the frequency in a single variable int type
            if class_name in event_counts:
                event_count = event_counts[class_name]
                # put event_count in the corresponding column of the event_type_counts dataframe
                event_type_counts[class_name] = event_count
                


    # save df to csv file
    event_type_counts.to_csv("detections.csv")

detect_events("/home/urvashi2022/Desktop/UI_DEVELOPMENT/DetectionMoreEvents/dataset/demo.mp4")


