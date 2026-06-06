#!/bin/bash
# YOLOv5 Cloud Application Deployment Script for EC2 Ubuntu Instance

echo "Updating system packages..."
sudo apt-get update -y

echo "Installing system dependencies for OpenCV and Python..."
sudo apt-get install -y python3-pip git libgl1-mesa-glx libglib2.0-0

echo "Cloning official Ultralytics YOLOv5 repository..."
if [ ! -d "yolov5" ]; then
    git clone https://github.com/ultralytics/yolov5.git
fi

cd yolov5
echo "Installing Python dependencies (PyTorch, OpenCV, Flask)..."
pip3 install -r requirements.txt
pip3 install flask opencv-python-headless numpy

echo "EC2 Environment Deployment configuration complete."
echo "To run the server execution context: python3 app.py"