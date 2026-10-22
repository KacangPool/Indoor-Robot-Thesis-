"""Detection selection/serialization; no model loading, ROS or publishers."""
import math


def finite_number(value):
    number = float(value)
    return number if not (math.isnan(number) or math.isinf(number)) else None


def boxes_list(message):
    return [{'class': str(box.Class), 'class_id': int(box.id),
             'score': finite_number(box.probability),
             'xmin': int(box.xmin), 'ymin': int(box.ymin),
             'xmax': int(box.xmax), 'ymax': int(box.ymax)}
            for box in message.bounding_boxes]


def select_person_boxes(boxes, threshold):
    selected = []
    for box in boxes:
        if box.Class != 'person':
            continue
        try:
            score = float(box.probability)
        except (TypeError, ValueError, OverflowError):
            continue
        if math.isnan(score) or math.isinf(score) or not 0 <= score <= 1:
            continue
        if score >= threshold:
            selected.append(box)
    return selected


def filtered_message(message, message_type, threshold):
    result = message_type()
    result.header = message.header
    result.image_header = message.image_header
    result.bounding_boxes = select_person_boxes(message.bounding_boxes, threshold)
    return result
