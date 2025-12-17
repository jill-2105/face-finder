import face_recognition
import cv2
import numpy as np
import os

# PHASE ADDING NEW IDENTITY
def add_individual(images_path, threshold):

    personalid = str(input("Enter your personalid :" + '\n'))
    image_full_personalid = personalid + '.png'

    if os.path.exists(os.path.join(images_path, image_full_personalid)):
        print("This personalid exists already please try another personalid !")
        return

    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cam = cv2.VideoCapture(0)
    
    while True:
        result, image = cam.read()
        if result:
            no_bounding_box_image = image.copy()
            individual_check = detect_bounding_box(image, face_classifier)
            cv2.imshow('Video', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Hardware Error !")
            cam.release()
            cv2.destroyAllWindows()
            return
        
    if type(individual_check) != tuple:
        known_face_encodings = []
        known_face_personalids = []
        for image in os.listdir(images_path):
            known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file(os.path.join(images_path, image)))[0])
            known_face_personalids.append(image[:-5])

        frame = no_bounding_box_image.copy()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
        face_encoding = face_recognition.face_encodings(rgb_small_frame, face_recognition.face_locations(rgb_small_frame))
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding[0])
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if face_distances[best_match_index] > threshold:
                    cv2.imwrite(os.path.join(images_path, image_full_personalid), no_bounding_box_image)
                    # cursor.execute("INSERT INTO employees (personalid) VALUES (%s)", (personalid))
                    # connection.commit()
            else:
                print("This individual is registered please try a new face !")
                cam.release()
                cv2.destroyAllWindows()
                return
        else:
            cv2.imwrite(os.path.join(images_path, image_full_personalid), no_bounding_box_image)
            # cursor.execute("INSERT INTO employees (personalid) VALUES (%s)", (personalid))
            # connection.commit()
    else:
        print("No face detected please put your face in front of the camera !")
        cam.release()
        cv2.destroyAllWindows()
        return

    if os.path.exists(os.path.join(images_path, image_full_personalid)):
        print(personalid + " saved successfully")
    else:
        print("Failed to save")

    cam.release()
    cv2.destroyAllWindows()


def detect_bounding_box(image, face_classifier):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 4)
    return(faces)
    

# PHASE e-KYC
def f_r(images_path, threshold):

    video_capture = cv2.VideoCapture(0)

    known_face_encodings = []
    known_face_personalids = []
    if len(os.listdir(images_path)) == 0:
        print("No image file in the source Directory")
        return
    
    for image in os.listdir(images_path):
        known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file(os.path.join(images_path, image)))[0])
        known_face_personalids.append(image[:-4])


    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_personalids = []
    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        if not ret:
            print("Hardware Error !")
            video_capture.release()
            cv2.destroyAllWindows()
            return

        # Only process every other frame of video to save time
        if process_this_frame:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
            
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_personalids = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                personalid = "Unknown"
                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     personalid = known_face_personalids[first_match_index]
                
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < threshold and matches[best_match_index]:
                    personalid = known_face_personalids[best_match_index]

                face_personalids.append(personalid)

        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), personalid in zip(face_locations, face_personalids):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a personalid below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, personalid, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        #     cursor.execute("UPDATE employees SET time = %s WHERE personalid = %s and personalid <> 'Unknown'", (str(datetime.datetime.now()), personalid))
        
        # connection.commit()
        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    images_path = "./photos/"
    threshold = 0.40

    # connection = psycopg2.connect(database="gregory", user="postgres", password="p1O3IbNds5hVmAyU", host="services.irn9.chabokan.net", port=41270)
    # cursor = connection.cursor()

    choice = 'dummy_input'
    while choice != '5':
        choice = input("1. Add individual " + '\n' + "2. Run e-KYC" + '\n' + "3. Print report" + '\n' + "4. Delete report" + '\n' + "5. Quit" + '\n')

        if choice == '1':
            add_individual(images_path, threshold)
        elif choice == '2':
            f_r(images_path, threshold)
        elif choice == '3':
            # cursor.execute("SELECT * FROM employees")
            # for i in cursor:
            #     print(i)
            pass
        elif choice == '4':
            # cursor.execute("DELETE FROM employees")
            # connection.commit()
            # print("Report deleted successfully")
            pass
        elif choice == '5':
            break
        else:
            print("Invalid choice, please try again !")

    
    # cursor.close()
