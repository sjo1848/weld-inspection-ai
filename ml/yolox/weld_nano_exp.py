from __future__ import annotations

import os

import torch.nn as nn
from yolox.exp import Exp as BaseExp


class Exp(BaseExp):
    """Bounded YOLOX-Nano transfer-learning experiment for WELD-VISION-001."""

    def __init__(self) -> None:
        super().__init__()
        self.depth = 0.33
        self.width = 0.25
        self.input_size = (416, 416)
        self.random_size = (10, 20)
        self.mosaic_scale = (0.5, 1.5)
        self.test_size = (416, 416)
        self.mosaic_prob = 0.5
        self.enable_mixup = False

        self.num_classes = 3
        self.data_dir = os.environ.get("WELD_YOLOX_DATA_DIR", "data/yolox/weld-v0.1")
        self.output_dir = os.environ.get("WELD_YOLOX_OUTPUT_DIR", "./YOLOX_outputs")
        self.train_ann = "instances_train.json"
        self.val_ann = "instances_val.json"
        self.test_ann = "instances_test.json"

        self.max_epoch = int(os.environ.get("WELD_YOLOX_EPOCHS", "80"))
        self.warmup_epochs = 3
        self.no_aug_epochs = 10
        self.eval_interval = 1
        self.data_num_workers = int(os.environ.get("WELD_YOLOX_WORKERS", "2"))
        self.seed = 20260915
        self.save_history_ckpt = False
        self.exp_name = "weld_nano_v0_1"

    def get_model(self, sublinear: bool = False):
        del sublinear

        def init_yolo(module):
            for layer in module.modules():
                if isinstance(layer, nn.BatchNorm2d):
                    layer.eps = 1e-3
                    layer.momentum = 0.03

        if "model" not in self.__dict__:
            from yolox.models import YOLOPAFPN, YOLOX, YOLOXHead

            in_channels = [256, 512, 1024]
            backbone = YOLOPAFPN(
                self.depth,
                self.width,
                in_channels=in_channels,
                act=self.act,
                depthwise=True,
            )
            head = YOLOXHead(
                self.num_classes,
                self.width,
                in_channels=in_channels,
                act=self.act,
                depthwise=True,
            )
            self.model = YOLOX(backbone, head)
        self.model.apply(init_yolo)
        self.model.head.initialize_biases(1e-2)
        return self.model
