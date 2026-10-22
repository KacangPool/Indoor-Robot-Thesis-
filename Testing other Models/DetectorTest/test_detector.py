"""Original laptop experiment entry point; safe to import without inference."""
from detector_model import load_detector, predict_image, annotate_prediction


def main():
    from PIL import Image
    model, weights = load_detector()
    image = Image.open('input.png').convert('RGB')
    prediction = predict_image(image, model, weights)
    result, count = annotate_prediction(image, prediction, weights.meta['categories'])
    result.save('result.png')
    print('Saved result.png with {} detections.'.format(count))


if __name__ == '__main__':
    main()
