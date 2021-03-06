import cv2  # OpenCV Library
# https://sublimerobots.com/2015/02/dancing-mustaches/
#-----------------------------------------------------------------------------
#       Load and configure Haar Cascade Classifiers
#-----------------------------------------------------------------------------

baseCascadePath = "./model/"
faceCascadeFilePath = baseCascadePath + "haarcascade_frontalface_default.xml"
noseCascadeFilePath = baseCascadePath + "haarcascade_mcs_nose.xml"

# build our cv2 Cascade Classifiers
faceCascade = cv2.CascadeClassifier(faceCascadeFilePath)
noseCascade = cv2.CascadeClassifier(noseCascadeFilePath)

#-----------------------------------------------------------------------------
#       Load and configure mustache (.png with alpha transparency)
#-----------------------------------------------------------------------------

# Load our overlay image: mustache.png
imgDecoration = cv2.imread('res/ironman.png',-1)

# Create the mask for the mustache
orig_mask = imgDecoration[:,:,3]

# Create the inverted mask for the mustache
# orig_mask_inv = cv2.bitwise_not(orig_mask)
orig_mask_inv = cv2.bitwise_not(orig_mask)
# Convert mustache image to BGR
# and save the original image size (used later when re-sizing the image)
imgDecoration = imgDecoration[:,:,0:3]
origDecorationHeight, origDecorationWidth = imgDecoration.shape[:2]
print origDecorationHeight, origDecorationWidth
#-----------------------------------------------------------------------------
#       Main program loop
#-----------------------------------------------------------------------------

# collect video input from first webcam on system
video_capture = cv2.VideoCapture(0)
video_capture.set(3, 320)
video_capture.set(4, 240)

while True:
    # Capture video feed
    ret, frame = video_capture.read()

    # Create greyscale image from the video feed
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    # Detect faces in input video stream
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

   # Iterate over each face found
    for (x, y, w, h) in faces:
        # Un-comment the next line for debug (draw box around all faces)
        # face = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        x1 = x
        y1 = y
        x2 = x + w
        y2 = y + h
        faceWidth = w
        faceHeight = h
        print "face area", faceWidth, faceHeight

        face_top, face_bottom, face_left, face_right = y1, y2, x1, x2

        roi_gray = gray[y1:y2, x1:x2]
        roi_color = frame[y1:y2, x1:x2]

        # Detect a nose within the region bounded by each face (the ROI)
        nose = noseCascade.detectMultiScale(roi_gray)

        for (nx,ny,nw,nh) in nose:
            # Un-comment the next line for debug (draw box around the nose)
            #cv2.rectangle(roi_color,(nx,ny),(nx+nw,ny+nh),(255,0,0),2)

            # The mustache should be three times the width of the nose
            DecorationWidth =  int(round(5 * faceWidth))
            DecorationHeight = DecorationWidth * origDecorationHeight / origDecorationWidth


            # Center the mustache on the bottom of the nose
            x1 = nx - (DecorationWidth/3)
            x2 = nx + nw + (DecorationWidth/3)
            y1 = ny + nh - (DecorationHeight/2)
            y2 = ny + nh + (DecorationHeight/2)

            # Check for clipping
            if x1 < 0:
                x1 = 0
            if y1 < 0:
                y1 = 0
            if x2 > w:
                x2 = w
            if y2 > h:
                y2 = h

            # Re-calculate the width and height of the mustache image
            DecorationWidth = x2 - x1
            DecorationHeight = y2 - y1 + 1
            print "Decorate area", DecorationWidth, DecorationHeight

            # Re-size the original image and the masks to the mustache sizes
            # calcualted above
            mustache = cv2.resize(imgDecoration, (DecorationWidth,DecorationHeight), interpolation = cv2.INTER_AREA)
            mask = cv2.resize(orig_mask, (DecorationWidth,DecorationHeight), interpolation = cv2.INTER_AREA)
            mask_inv = cv2.resize(orig_mask_inv, (DecorationWidth,DecorationHeight), interpolation = cv2.INTER_AREA)

            # take ROI for mustache from background equal to size of mustache image
            roi = roi_color[y1:y2, x1:x2]

            # roi_bg contains the original image only where the mustache is not
            # in the region that is the size of the mustache.
            roi_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)

            # roi_fg contains the image of the mustache only where the mustache is
            roi_fg = cv2.bitwise_and(mustache,mustache,mask = mask)

            # join the roi_bg and roi_fg
            dst = cv2.add(roi_bg,roi_fg)

            # place the joined image, saved to dst back over the original image
            roi_color[y1:y2, x1:x2] = dst

            break

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # press any key to exit
    # NOTE;  x86 systems may need to remove: " 0xFF == ord('q')"
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()