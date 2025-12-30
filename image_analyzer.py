import cv2
from PIL import Image
import numpy as np
import os

class ImageAnalyzer:
    def __init__(self):
        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        if self.face_cascade.empty():
            raise RuntimeError(f"Could not load face cascade from {face_cascade_path}")
    
    def analyze_photo(self, image_path):
        """Analyze photo and extract roastable features"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        features = {
            'faces': self._detect_faces(image),
            'objects': self._detect_objects(image),
            'colors': self._analyze_colors(rgb_image),
            'composition': self._analyze_composition(image)
        }
        
        return features
    
    def _detect_faces(self, image):
        """Detect faces and analyze facial features"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        face_features = []
        for (x, y, w, h) in faces:
            features = {
                'width': w,
                'height': h,
                'ratio': w / h if h > 0 else 1,
                'size': 'large' if w > 200 else 'small' if w < 100 else 'medium'
            }
            face_features.append(features)
        
        return {'count': len(faces), 'features': face_features}
    
    def _detect_objects(self, image):
        """Simple object detection for common roastable items"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect eyes and faces for object inference
        eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
        eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        if eye_cascade.empty():
            eyes = []  # Fallback if eye cascade fails
        else:
            eyes = eye_cascade.detectMultiScale(gray, 1.1, 3)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        objects = {
            'glasses': len(eyes) > len(faces) * 2,  # More eyes than expected might indicate glasses
            'multiple_people': len(faces) > 1
        }
        
        return objects
    
    def _analyze_colors(self, rgb_image):
        """Analyze dominant colors in the image"""
        # Sample pixels for efficiency
        h, w = rgb_image.shape[:2]
        sample = rgb_image[::max(1, h//100), ::max(1, w//100)]
        dominant_color = np.mean(sample.reshape(-1, 3), axis=0)
        
        # Categorize colors
        r, g, b = dominant_color
        brightness = np.mean(dominant_color)
        
        if brightness > 200:
            color_theme = 'bright'
        elif brightness < 50:
            color_theme = 'dark'
        elif r > g + 30 and r > b + 30:
            color_theme = 'red'
        elif g > r + 30 and g > b + 30:
            color_theme = 'green'
        elif b > r + 30 and b > g + 30:
            color_theme = 'blue'
        else:
            color_theme = 'mixed'
        
        return {'theme': color_theme, 'brightness': float(brightness)}
    
    def _analyze_composition(self, image):
        """Analyze image composition for roasting material"""
        height, width = image.shape[:2]
        
        return {
            'aspect_ratio': width / height,
            'resolution': 'low' if width < 500 else 'high',
            'orientation': 'landscape' if width > height else 'portrait'
        }