# Track football players with YOlOv5 and ByteTrack <!-- omit from toc -->


Football automated analytics is hot topics in the intersection between AI and sports. In this project, we build a tool for detecting and tracking football players, referees and ball in videos. For this we use [YOLOv5](https://github.com/ultralytics/ultralytics) (a popular and fast object detector) for detecting the players in each frame of the video, and [ByteTrack](https://github.com/ifzhang/ByteTrack) a multi object detection model released in 2022 to identify the players and track their trajectory.

## YOLOv5 training

The first part of the project is to train YOLOv5 on detecting players in images.
The model was trained for 300 epochs on 204 images with a resolution of 640x640.

The model has trouble detecting the ball due to its small size. One of the solutions is to increase the network resolution to 1280x1280. However, it requires resources beyond my reach.  
The alternative was to train a YOLOv5m on 1280 resolution. Evaluation tables bellow show that has 60% better mAP50-95. However, it confuses the referees and players more often (as seen on the demo video).

## Tracking the players with ByteTrack

The second part is running yolo inference on each frame of the video and then track the detections with ByteTrack:
ByteTrack works well when no others are nearby and loses the identity of the players if they form a cluster. This is one of the challenges of object tracking.

The accuracy of the tracking depends heavily on yolo performance. Training on a large dataset would enhance the this solution.

### The Backbone
The backbone network extract the important features from the images at different levels. It is composed of series of ``ConvBlock`` and ``CSPLayer_2``. The CSPLayer is made of residuals blocks whose filters are concatenated to form rich features.

### The Neck
The neck is a feature pyramid network. This family of networks take as input the features of the backbone at low resolutions (the bottom-up pathway) and reconstruct them by up-scaling and applying convolution blocks between the layers. Lateral connection are added to ease the training (they function as residual connection) and compensate for the lost information due to the down-scaling and up-scaling.

### The loss 
The loss function is as follows:

$$
\begin{gathered}
loss = \lambda_1 L_{box} + \lambda_2 L_{cls} + \lambda_3 L_{dfl} \\
\end{gathered}
$$

The $L_{cls}$ is a Cross Entropy loss applied on the class.

The $L_{box}$ is CIoU loss, it aims to:

* Increase the overlapping area of the ground truth box and the predicted box.
* Minimize their central point distance.
* Maintain the consistency of the boxes aspect ratio.


The CIoU loss function can be defined as

$$
\mathcal{L}_{C I o U}=1-I o U+\frac{\rho^2\left(b, b^{g t}\right)}{c^2}+\alpha v .
$$

where $b$ and $b^{gt}$ denote the central points of prediction and of ground truth, $\rho$ is the Euclidean distance, and $c$ is the diagonal length of the smallest enclosing box covering the two boxes. The trade-off parameter $\alpha$ is defined as

$$
\alpha=\frac{v}{(1-I o U)+v}
$$

and $v$ measures the consistency of a aspect ratio,

$$
v=\frac{4}{\pi}\left(\arctan \frac{w^{g t}}{h^{g t}}-\arctan \frac{w}{h}\right)^2 .
$$

The $L_{dfl}$ is distributional focal loss.

## ByteTrack explained

ByteTrack is a Multi Object Tracker, it identifies the detected objects and tracks their trajectory in the video. The algorithm uses tracklets, representation of tracked objects, to store the identity of detections.

The main idea of BYTE (the algorithm behind ByteTrack), is to consider both high and low confidence detections.  
For each frame the position of the bounding boxes are predicted using a Kalman filter from the previous positions. The high confidence detections $D^{high}$ are matched with these predicted tracklets by iou and are identified.  
The low confidence detection $D^{low}$ are compared with unmatched tracklets (identified objects are not associated to any bounding box in that frame). This helps identity occulted objects.  
A bin of unmatched tracklets is kept for $n$ frames to handle object rebirth. They are deleted beyond $n$ is they remain unmatched.
