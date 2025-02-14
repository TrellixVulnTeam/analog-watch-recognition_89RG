import os
from pathlib import Path
from typing import List, Tuple

import click
import cv2
import numpy as np
import tensorflow as tf
import tensorflow.python.keras.backend as K
from dvclive.keras import DvcLiveCallback
from PIL import Image
from segmentation_models.metrics import IOUScore
from tensorflow_serving.apis import model_pb2, predict_pb2, prediction_log_pb2

from watch_recognition.label_studio_adapters import (
    load_label_studio_polygon_detection_dataset,
)
from watch_recognition.models import get_segmentation_model
from watch_recognition.utilities import Polygon
from watch_recognition.visualization import visualize_masks

os.environ["SM_FRAMEWORK"] = "tf.keras"


def TverskyLoss(targets, inputs, alpha=0.5, beta=0.5, smooth=1e-6):
    # https://www.kaggle.com/bigironsphere/loss-function-library-keras-pytorch
    # flatten label and prediction tensors
    inputs = K.flatten(inputs)
    targets = K.flatten(targets)

    # True Positives, False Positives & False Negatives
    TP = K.sum((inputs * targets))
    FP = K.sum(((1 - targets) * inputs))
    FN = K.sum((targets * (1 - inputs)))

    Tversky = (TP + smooth) / (TP + alpha * FP + beta * FN + smooth)

    return 1 - Tversky


def encode_polygon_to_mask(
    polygons: List[Polygon], n_labels: int, mask_size: Tuple[int, int]
) -> np.ndarray:
    mask = np.zeros((*mask_size, n_labels))
    for polygon in polygons:
        poly_mask = polygon.to_binary_mask(shape=mask_size)
        cls = int(polygon.name)
        mask[:, :, cls] += poly_mask
    return (mask > 0).astype(np.float32)


@click.command()
@click.option("--epochs", default=1, type=int)
@click.option("--batch-size", default=32, type=int)
@click.option("--image-size", default=96, type=int)
@click.option("--max-images", default=None, type=int)
@click.option("--seed", default=None, type=int)
@click.option("--confidence-threshold", default=0.5, type=float)
@click.option("--verbosity", default=1, type=int)
@click.option(
    "--fine-tune-from-checkpoint",
    is_flag=True,
    help="Use previous model's weight to initialize the model. "
    "If not set ImageNet weights are used instead.",
)
def main(
    epochs: int,
    batch_size: int,
    image_size: int,
    max_images: int,
    seed: int,
    confidence_threshold: float,
    verbosity: int,
    fine_tune_from_checkpoint: bool,
):
    if seed is not None:
        tf.keras.utils.set_random_seed(seed)
    label_to_cls = {
        "Hands": 0,
    }
    # TODO this should be in params.yaml
    dataset_path = Path("datasets/watch-faces-local.json")
    cls_to_label = {v: k for k, v in label_to_cls.items()}
    num_classes = len(label_to_cls)
    image_size = (image_size, image_size)
    # TODO new data loader - augment before cropping
    bbox_labels = ["WatchFace"]
    checkpoint_path = Path("checkpoints/segmentation/checkpoint")
    crop_size = image_size
    dataset_train = list(
        load_label_studio_polygon_detection_dataset(
            dataset_path,
            crop_size=crop_size,
            bbox_labels=bbox_labels,
            label_mapping=label_to_cls,
            max_num_images=max_images,
            split="train",
        )
    )
    X = []
    y = []
    for img, polygons in dataset_train:
        X.append(img)
        y.append(encode_polygon_to_mask(polygons, len(label_to_cls), crop_size))

    X = np.array(X)
    y = np.array(y)
    print(X.shape, y.shape)

    dataset_val = list(
        load_label_studio_polygon_detection_dataset(
            dataset_path,
            crop_size=crop_size,
            bbox_labels=bbox_labels,
            label_mapping=label_to_cls,
            max_num_images=max_images,
            split="val",
        )
    )
    X_val = []
    y_val = []
    for img, polygons in dataset_val:
        X_val.append(img)
        y_val.append(encode_polygon_to_mask(polygons, len(label_to_cls), crop_size))

    X_val = np.array(X_val)
    y_val = np.array(y_val)
    print(X_val.shape, y_val.shape)

    train_model = get_segmentation_model(
        image_size=image_size,
        n_outputs=num_classes,
        backbone="efficientnetb0",
    )
    train_model.summary()
    optimizer = tf.keras.optimizers.Adam(1e-3)
    loss = TverskyLoss
    train_model.compile(
        loss=loss,
        optimizer=optimizer,
        metrics=[
            IOUScore(),
        ],
    )
    if fine_tune_from_checkpoint and checkpoint_path.exists():
        train_model.load_weights(checkpoint_path)
    callbacks_list = [DvcLiveCallback(path="metrics/segmentation")]
    if not fine_tune_from_checkpoint:
        callbacks_list.append(
            tf.keras.callbacks.ModelCheckpoint(
                checkpoint_path,
                monitor="val_loss",
                verbose=1,
                save_best_only=True,
                save_weights_only=True,
                mode="auto",
                save_freq="epoch",
            ),
        )
    # -- train model
    train_model.fit(
        X,
        y,
        epochs=epochs,
        validation_data=(X_val, y_val),
        callbacks=callbacks_list,
        verbose=verbosity,
        batch_size=batch_size,
    )

    #  -- export inference-only model
    image = tf.keras.Input(shape=[None, None, 3], name="image")
    # TODO layer with uint8 -> float conversion
    resized_image = tf.keras.layers.Resizing(
        crop_size[0], crop_size[1], interpolation="bilinear", crop_to_aspect_ratio=False
    )(image)
    inference_model = get_segmentation_model(
        image_size=image_size,
        n_outputs=num_classes,
        backbone="efficientnetb0",
    )

    predictions = inference_model(resized_image)
    # TODO name outputs
    inference_model = tf.keras.Model(inputs=image, outputs=predictions)
    inference_model.set_weights(train_model.get_weights())
    model_save_path = Path("models/segmentation/")
    inference_model.save(model_save_path)

    # run on a single example image for sanity check if exported detector is working
    example_image_path = Path("example_data/test-image-2.jpg")
    save_file = Path(f"example_predictions/segmentation/{example_image_path.name}")
    save_file.parent.mkdir(exist_ok=True)

    with Image.open(example_image_path) as img:
        image_np = np.array(img).astype(np.float32)

    input_image = np.expand_dims(image_np, axis=0)

    results = inference_model.predict(input_image, verbose=0)[0]
    masks = []
    for cls, name in cls_to_label.items():
        mask = results[:, :, cls] > confidence_threshold
        mask = cv2.resize(
            mask.astype("uint8"),
            image_np.shape[:2][::-1],
            interpolation=cv2.INTER_NEAREST,
        ).astype("bool")
        masks.append(mask)

    visualize_masks(image_np, masks, savefile=save_file)

    warmup_tf_record_file = (
        model_save_path / "assets.extra" / "tf_serving_warmup_requests"
    )
    warmup_tf_record_file.parent.mkdir(exist_ok=True, parents=True)
    with tf.io.TFRecordWriter(str(warmup_tf_record_file)) as writer:
        tensor_proto = tf.make_tensor_proto(input_image)
        request = predict_pb2.PredictRequest(
            model_spec=model_pb2.ModelSpec(signature_name="serving_default"),
            inputs={"image": tensor_proto},
        )
        log = prediction_log_pb2.PredictionLog(
            predict_log=prediction_log_pb2.PredictLog(request=request)
        )
        writer.write(log.SerializeToString())


if __name__ == "__main__":
    main()
