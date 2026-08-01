import cv2
from datetime import datetime


def extract_detections(result, model_names):
    """
    Extract persons, helmets and vests
    from YOLO tracking results.
    """

    persons = []
    helmets = []
    vests = []

    if result.boxes is None or len(result.boxes) == 0:
        return persons, helmets, vests

    # Minimum size thresholds to filter false positives
    # Reduced to allow smaller/distant workers
    MIN_PERSON_WIDTH = 30
    MIN_PERSON_HEIGHT = 60
    MIN_PERSON_AREA = 2000

    for box in result.boxes:

        cls = int(box.cls[0])
        class_name = model_names[cls]

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # Validate box coordinates
        if x2 <= x1 or y2 <= y1:
            continue

        track_id = None

        if box.id is not None:
            track_id = int(box.id[0])

        confidence = float(box.conf[0])

        detection = {
            "id": track_id,
            "box": (x1, y1, x2, y2),
            "confidence": confidence
        }

        if class_name == "person":
            # Calculate box dimensions
            box_width = x2 - x1
            box_height = y2 - y1
            box_area = box_width * box_height
            
            # Filter out small/invalid person detections
            if (box_width < MIN_PERSON_WIDTH or 
                box_height < MIN_PERSON_HEIGHT or 
                box_area < MIN_PERSON_AREA):
                continue
            
            # Only include persons with valid tracking IDs
            if track_id is not None:
                persons.append(detection)

        elif class_name == "helmet":
            helmets.append(detection)

        elif class_name == "vest":
            vests.append(detection)

    return persons, helmets, vests


def draw_box(frame, box, color, text):

    x1, y1, x2, y2 = box
    
    # Ensure coordinates are integers and valid
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
    # Validate box dimensions
    if x2 <= x1 or y2 <= y1:
        print(f"[WARNING] Invalid box coordinates: {box}")
        return

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        color,
        3  # Thicker line for better visibility
    )

    # Background for text
    (text_width, text_height), baseline = cv2.getTextSize(
        text, 
        cv2.FONT_HERSHEY_SIMPLEX, 
        0.6, 
        2
    )
    
    cv2.rectangle(
        frame,
        (x1, max(y1 - text_height - 10, 0)),
        (x1 + text_width, max(y1, text_height + 10)),
        color,
        -1
    )

    cv2.putText(
        frame,
        text,
        (x1, max(y1 - 5, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


def get_timestamp():

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def resize_frame(frame, width=1280):

    h, w = frame.shape[:2]

    if w <= width:
        return frame

    ratio = width / w

    height = int(h * ratio)

    return cv2.resize(frame, (width, height))