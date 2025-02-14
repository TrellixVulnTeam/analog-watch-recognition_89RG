from typing import List

import cv2
import numpy as np
from distinctipy import distinctipy
from matplotlib import pyplot as plt

from watch_recognition.utilities import Point


def visualize_keypoints(image: np.ndarray, points: List[Point], savefile=None):
    plt.figure()
    plt.tight_layout()
    plt.axis("off")
    plt.imshow(image)
    colors = ["red", "green", "blue"]
    ax = plt.gca()
    for point, color in zip(points, colors):
        point.plot(color=color, size=30, ax=ax)
    plt.legend()
    if savefile is not None:
        plt.savefig(savefile, bbox_inches="tight")
    return ax


def visualize_masks(image: np.ndarray, masks: List[np.ndarray], savefile=None):
    plt.figure()
    plt.tight_layout()
    plt.axis("off")
    colors = distinctipy.get_colors(len(masks))
    overlay = image.astype("uint8")
    ax = plt.gca()
    for mask, color in zip(masks, colors):
        img = np.zeros(shape=(*mask.shape[:2], 3)).astype("uint8")
        img[mask] = np.array(color).astype("uint8") * 255
        overlay = cv2.addWeighted(overlay, 0.8, img, 0.2, 0)
    ax.imshow(overlay)
    if savefile is not None:
        plt.savefig(savefile, bbox_inches="tight")
    return ax
