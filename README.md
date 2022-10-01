# Graph
```mermaid
flowchart TD
	node1["datasets/watch-faces.json.dvc"]
	node2["download-images"]
	node3["eval-detector"]
	node4["eval-end-2-end"]
	node5["eval-keypoint"]
	node6["eval-segmentation"]
	node7["train-detector"]
	node8["train-keypoint"]
	node9["train-segmentation"]
	node10["update-metrics"]
	node1-->node2
	node2-->node4
	node2-->node7
	node2-->node8
	node2-->node9
	node3-->node10
	node4-->node10
	node5-->node10
	node7-->node3
	node7-->node4
	node7-->node5
	node7-->node6
	node7-->node10
	node8-->node4
	node8-->node5
	node8-->node10
	node9-->node4
	node9-->node6
	node9-->node10
	node11["checkpoints/segmentation.dvc"]
	node12["checkpoints/detector.dvc"]
	node13["checkpoints/keypoint.dvc"]
```
# Metrics
| Path                           | train.1-min_acc   | train.10-min_acc   | train.60-min_acc   | val.1-min_acc   | val.10-min_acc   | val.60-min_acc   |
|--------------------------------|-------------------|--------------------|--------------------|-----------------|------------------|------------------|
| metrics/end_2_end_summary.json | 0.166             | 0.247              | 0.462              | 0.065           | 0.104            | 0.156            |

| Path                             | AP @IoU=0.50   | AP @IoU=0.50:0.95   | AP @IoU=0.75   | AP @IoU=0.95   | AR @maxDets=1   | AR @maxDets=10   | AR @maxDets=100   | Num Images   | eval.MeanAveragePrecision   | eval.Recall   | eval.box_loss   | eval.classification_loss   | eval.loss   | eval.regularization_loss   | step   | train.box_loss   | train.classification_loss   | train.loss   | train.regularization_loss   |
|----------------------------------|----------------|---------------------|----------------|----------------|-----------------|------------------|-------------------|--------------|-----------------------------|---------------|-----------------|----------------------------|-------------|----------------------------|--------|------------------|-----------------------------|--------------|-----------------------------|
| metrics/detector.json            | -              | -                   | -              | -              | -               | -                | -                 | -            | 0.341                       | 0.555         | 3.218           | 2.475                      | 5.693       | 0.0                        | 99     | 0.62             | 0.211                       | 0.83         | 0.0                         |
| metrics/detector/coco_train.json | 0.865          | 0.753               | 0.865          | -1.0           | 0.844           | 0.899            | 0.899             | 221          | -                           | -             | -               | -                          | -           | -                          | -      | -                | -                           | -            | -                           |
| metrics/detector/coco_val.json   | 0.731          | 0.434               | 0.471          | -1.0           | 0.528           | 0.621            | 0.621             | 36           | -                           | -             | -               | -                          | -           | -                          | -      | -                | -                           | -            | -                           |

| Path                             | AP @IoU=0.50   | AP @IoU=0.50:0.95   | AP @IoU=0.75   | AR @IoU=0.50   | AR @IoU=0.50:0.95   | AR @IoU=0.75   | Num Images   | eval.iou_score   | eval.loss   | step   | train.iou_score   | train.loss   |
|----------------------------------|----------------|---------------------|----------------|----------------|---------------------|----------------|--------------|------------------|-------------|--------|-------------------|--------------|
| metrics/keypoint.json            | -              | -                   | -              | -              | -                   | -              | -            | 0.461            | 0.531       | 99     | 0.911             | 0.088        |
| metrics/keypoint/coco_train.json | 0.737          | 0.528               | 0.42           | 0.903          | 0.748               | 0.665          | 221          | -                | -           | -      | -                 | -            |
| metrics/keypoint/coco_val.json   | 0.61           | 0.299               | 0.189          | 0.793          | 0.538               | 0.448          | 36           | -                | -           | -      | -                 | -            |

| Path                      | eval.iou_score   | eval.loss   | step   | train.iou_score   | train.loss   |
|---------------------------|------------------|-------------|--------|-------------------|--------------|
| metrics/segmentation.json | 0.603            | 0.249       | 99     | 0.818             | 0.1          |

## End 2 end metrics definitions
Final metric for the entire system is 'x-min accuracy' which is the fraction of system predictions accurate within x minutes. Example:  
$$\text{1-min-acc} = 1 - {|{|time - {time}_{pred}| < 1min}| \over N_{samples}}$$
# Demo - version 2

<img src="example_data/IMG_0039_render.jpg?raw=true" width=400> <img src="example_data/IMG_0040_render.jpg?raw=true" width=400>

<img src="example_data/Zrzut%20ekranu%202021-08-25%20o%2022.24.14_render.jpg?raw=true" width=400> <img src="example_data/Zrzut%20ekranu%202021-08-25%20o%2022.24.24_render.jpg?raw=true" width=400 >


https://user-images.githubusercontent.com/17779555/151705227-a892424b-279c-4a43-9076-494a55717d0c.mov

models used:
- bbox detector for finding clock face in the image
- classifier for clock orientation estimation
- keypoint detection for center and top
- semantic segmentation for finding clock hands
- KDE for splitting the binary segmentation mask into individual clock hands
### Watch crop with center and top keypoint
![Alt text](example_data/crop_and_center.jpg?raw=true "Watch crop with center and top")
### Detected mask of watch hands
![Alt text](example_data/hands_mask.jpg?raw=true "Detected mask of watch hands")
### KDE of pixel angles
![Alt text](example_data/debug_plots.jpg?raw=true "KDE of pixel angles")
### Fitted lines to segmented pixels
![Alt text](example_data/fitted_lines.jpg?raw=true "Fitted lines to segmented pixels")
### Final selected and rejected lines
![Alt text](example_data/selected_lines.jpg?raw=true "Selected and rejected lines")

## Installation
Install `watch_recognition` module, run pip in the main repository dir
```bash
pip install watch_recognition/
```
Tested on Python 3.7 and 3.8
## Running models
Checkout example notebook: `notebooks/demo-on-examples.ipynb`
## Models description
_TODO_

# Demo - version 1

https://user-images.githubusercontent.com/17779555/136506927-d326381b-6d54-4c2a-91a8-aa0fee89ba36.mov

models used:
- bbox detector for finding clock face in the image
- classifier for clock orientation
- keypoint detection for center, top and end of clock hands

# Downloading images from OpenImage Dataset

```bash
wget https://raw.githubusercontent.com/openimages/dataset/master/downloader.py
```

```bash
python scripts/downloader.py ./download_data/train_ids_small.txt --download_folder=./download_data/train/
```

```bash
python scripts/downloader.py ./download_data/test_ids_small.txt --download_folder=./download_data/test/
```

```bash
python scripts/downloader.py ./download_data/validation_ids_small.txt --download_folder=./download_data/validation/
```
# Convert tagged data into keypoint dataset

see notebook `./notebooks/generate_kp_dataset.ipynb`

# Train keypoint detection model
see notebook `./notebooks/cell-coder.ipynb.ipynb`

# Label Studio setup
https://labelstud.io/

```xml
<View>
    <Image name="image" value="$image" zoom="true" zoomControl="true"/>
      <KeyPointLabels name="kp" toName="image">
        <Label value="Center" background="#FFA39E"/>
        <Label value="Top" background="#D4380D"/>
        <Label value="Crown" background="#FFC069"/>
    </KeyPointLabels>
    <PolygonLabels name="polygon" toName="image" strokeWidth="3" pointSize="small" opacity="0.9">
        <Label value="Hands" background="#45fc03"/>
    </PolygonLabels>
    <RectangleLabels name="bbox" toName="image">
        <Label value="WatchFace" background="#FFA39E"/>
    </RectangleLabels>
      <TextArea name="transcription" toName="image" editable="true" perRegion="true" required="false" maxSubmissions="1" rows="5" placeholder="Recognized Time" displayMode="region-list"/>    
</View>
```
References 
1. OpenImagesDataset https://opensource.google/projects/open-images-dataset
