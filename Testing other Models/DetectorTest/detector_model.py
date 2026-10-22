"""Reusable optional laptop SSDLite experiment; importing never loads a model.

The robot's YOLO is unchanged. Loading pretrained weights is explicit and may
download them if they are not already cached.
"""


def load_detector():
    from torchvision.models.detection import (
        ssdlite320_mobilenet_v3_large,
        SSDLite320_MobileNet_V3_Large_Weights,
    )
    weights = SSDLite320_MobileNet_V3_Large_Weights.COCO_V1
    model = ssdlite320_mobilenet_v3_large(weights=weights)
    model.eval()
    return model, weights


def predict_image(image, model, weights, torch_module=None):
    if torch_module is None:
        import torch as torch_module
    tensor = weights.transforms()(image)
    with torch_module.inference_mode():
        return model([tensor])[0]


def annotate_prediction(image, prediction, categories, threshold=0.5,
                        emit=print, draw_factory=None):
    if draw_factory is None:
        from PIL import ImageDraw
        draw_factory = ImageDraw.Draw
    result = image.copy()
    draw = draw_factory(result)
    count = 0
    for box, label, score in zip(prediction['boxes'], prediction['labels'], prediction['scores']):
        if float(score) < threshold:
            continue
        caption = '{}: {:.2f}'.format(categories[int(label)], float(score))
        coordinates = box.tolist()
        draw.rectangle(coordinates, outline='lime', width=3)
        draw.text((coordinates[0], coordinates[1]), caption, fill='red')
        emit(caption)
        count += 1
    return result, count
