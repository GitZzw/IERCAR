import cv2
import pyrealsense2 as rs
import numpy as np
import os
import time
import socket
import torch
import argparse
from nanodet.util import cfg, load_config, Logger
from nanodet.model.arch import build_model
from nanodet.util import load_model_weight
from nanodet.data.transform import Pipeline

image_ext = ['.jpg', '.jpeg', '.webp', '.bmp', '.png']
video_ext = ['mp4', 'mov', 'avi', 'mkv']

'''目标检测-图片'''
# python detect_main.py image --config ./config/nanodet-m.yml --model model/nanodet_m.pth --path  street.png

'''目标检测-视频文件'''
# python detect_main.py video --config ./config/nanodet-m.yml --model model/nanodet_m.pth --path  test.mp4

'''目标检测-摄像头'''
# python detect_main.py webcam --config ./config/nanodet-m.yml --model model/nanodet_m.pth --path  0

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('demo', default='image', help='demo type, eg. image, video and webcam')
    parser.add_argument('--config', help='model config file path')
    parser.add_argument('--model', help='model file path')
    parser.add_argument('--path', default='./demo', help='path to images or video')
    parser.add_argument('--camid', type=int, default=0, help='webcam demo camera id')
    args = parser.parse_args()
    return args


class Predictor(object):
    def __init__(self, cfg, model_path, logger, device='cuda:0'):
        self.cfg = cfg
        self.device = device
        model = build_model(cfg.model)
        ckpt = torch.load(model_path, map_location=lambda storage, loc: storage)
        load_model_weight(model, ckpt, logger)
        self.model = model.to(device).eval()
        self.pipeline = Pipeline(cfg.data.val.pipeline, cfg.data.val.keep_ratio)

    def inference(self, img):
        img_info = {}
        if isinstance(img, str):
            img_info['file_name'] = os.path.basename(img)
            img = cv2.imread(img)
        else:
            img_info['file_name'] = None

        height, width = img.shape[:2]
        img_info['height'] = height
        img_info['width'] = width
        meta = dict(img_info=img_info,
                    raw_img=img,
                    img=img)
        meta = self.pipeline(meta, self.cfg.data.val.input_size)
        meta['img'] = torch.from_numpy(meta['img'].transpose(2, 0, 1)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            results = self.model.inference(meta)
        return meta, results

    def visualize(self, dets, meta, class_names, score_thres, wait=0):
        time1 = time.time()
        self.model.head.show_result(meta['raw_img'], dets, class_names, score_thres=score_thres, show=True)
        #print('viz time: {:.3f}s'.format(time.time()-time1))


def get_image_list(path):
    image_names = []
    for maindir, subdir, file_name_list in os.walk(path):
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)
            ext = os.path.splitext(apath)[1]
            if ext in image_ext:
                image_names.append(apath)
    return image_names


def main():
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind(('127.0.0.1',8000))
    server.listen(5)
    print("waiting msg ...")
    conn, clint_add = server.accept()

    args = parse_args()
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True

    load_config(cfg, args.config)
    logger = Logger(-1, use_tensorboard=False)
    predictor = Predictor(cfg, args.model, logger, device='cuda:0')
    logger.log('Press "Esc", "q" or "Q" to exit.')
    if args.demo == 'image':
        if os.path.isdir(args.path):
            files = get_image_list(args.path)
        else:
            files = [args.path]
        files.sort()
        for image_name in files:
            meta, res = predictor.inference(image_name)
            predictor.visualize(res, meta, cfg.class_names, 0.35)
            ch = cv2.waitKey(0)
            if ch == 27 or ch == ord('q') or ch == ord('Q'):
                break
    elif args.demo == 'video' or args.demo == 'webcam':
        pipeline = rs.pipeline()
        # 创建 config 对象：
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        # Start streaming
        pipeline.start(config)
        #cap = cv2.VideoCapture(args.path if args.demo == 'video' else args.camid)
        while True:
            next_frames = pipeline.wait_for_frames()
            get_next_color_frame = next_frames.get_color_frame()
            frame = np.asanyarray(get_next_color_frame.get_data())
            meta, res = predictor.inference(frame)

            predictor.visualize(res, meta, cfg.class_names, 0.70)
            all_box = []
            for label in res:
                for bbox in res[label]:           
                    score = bbox[-1]
                    if score>0.70:
                        x0, y0, x1, y1 = [int(i) for i in bbox[:4]]
                        all_box.append([label, x0, y0, x1, y1, score])
            all_box.sort(key=lambda v: v[5])

            
            send_data_byte = bytes(0)
            time.sleep(0.005)
            if len(all_box) == 0:
                leftup_rightdown_corner = [-1, 0, 0, 0, 0,time.time(),'b']
                for i in range(len(leftup_rightdown_corner)):
                    #print(pickup_leftup_rightdown_corner[i])
                    pickup_senddata = str(leftup_rightdown_corner[i]) + ','
                    # print(pickup_senddata.encode())
                    send_data_byte += pickup_senddata.encode()
                    # print(send_data_byte)
                conn.send(send_data_byte)
            else:
                zzw = all_box[-1]
                label, x0, y0, x1, y1, score = zzw
                leftup_rightdown_corner = [1, x0, y0, x1, y1,time.time(),'a']
                for i in range(len(leftup_rightdown_corner)):
                    target_senddata = str(leftup_rightdown_corner[i]) + ','
                    send_data_byte += target_senddata.encode()
                conn.send(send_data_byte)


            ch = cv2.waitKey(1)
            if ch == 27 or ch == ord('q') or ch == ord('Q'):
                break


if __name__ == '__main__':
    main()
