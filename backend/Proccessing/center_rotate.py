import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional, List


class ImageProcessor:
    """
    A class for processing images with capabilities for:
    - Extracting largest regions
    - Centering objects
    - Adding transparency
    - Rotating images based on detected lines
    """
    
    def __init__(self, image_path: Optional[str] = None):
        """
        Initialize the ImageProcessor.
        
        Args:
            image_path (str, optional): Path to the image file
        """
        self.original_image = None
        self.processed_image = None
        
        if image_path:
            self.load_image(image_path)
    
    def load_image(self, image_path: str, with_alpha: bool = False) -> None:
        """
        Load an image from file.
        
        Args:
            image_path (str): Path to the image file
            with_alpha (bool): Whether to load with alpha channel
        """
        if with_alpha:
            self.original_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        else:
            self.original_image = cv2.imread(image_path)
        
        if self.original_image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        self.processed_image = self.original_image.copy()
    
    def extract_largest_region(self, threshold: int = 10) -> np.ndarray:
        """
        Extract the largest non-black region from the image.
        
        Args:
            threshold (int): Threshold value for binary conversion
            
        Returns:
            np.ndarray: Image with only the largest region
        """
        if self.processed_image is None:
            raise ValueError("No image loaded. Use load_image() first.")
        
        # Convert to grayscale and create mask
        gray = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            raise ValueError("No contours found in the image")
        
        # Find largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Create mask for largest contour
        largest_mask = np.zeros_like(gray)
        cv2.drawContours(largest_mask, [largest_contour], -1, 255, -1)
        
        # Extract the region
        result = cv2.bitwise_and(self.processed_image, self.processed_image, mask=largest_mask)
        
        self.processed_image = result
        return result
    
    def extract_rectangular_region(self, threshold: int = 10, aspect_ratio_filter: bool = True) -> np.ndarray:
        """
        Extract rectangular regions and filter out triangular/irregular parts.
        
        Args:
            threshold (int): Threshold value for binary conversion
            aspect_ratio_filter (bool): Whether to filter by aspect ratio
            
        Returns:
            np.ndarray: Image with rectangular region only
        """
        if self.processed_image is None:
            raise ValueError("No image loaded. Use load_image() first.")
        
        # Convert to grayscale and create mask
        gray = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            raise ValueError("No contours found in the image")
        
        # Filter contours based on rectangularity and size
        rectangular_contours = []
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Calculate contour area and bounding rectangle area
            contour_area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            rect_area = w * h
            
            # Check if contour is roughly rectangular
            # (contour area should be close to bounding rectangle area)
            rectangularity = contour_area / rect_area if rect_area > 0 else 0
            
            # Filter based on rectangularity and size
            if (rectangularity > 0.7 and  # At least 70% rectangular
                contour_area > 1000 and   # Minimum size
                len(approx) >= 4):        # At least 4 corners
                
                if aspect_ratio_filter:
                    # Check aspect ratio (width should be greater than height for fabric)
                    aspect_ratio = w / h if h > 0 else 0
                    if aspect_ratio > 1.5:  # Width is at least 1.5x height
                        rectangular_contours.append((contour, contour_area))
                else:
                    rectangular_contours.append((contour, contour_area))
        
        if not rectangular_contours:
            # Fallback to largest contour if no rectangular ones found
            largest_contour = max(contours, key=cv2.contourArea)
        else:
            # Get the largest rectangular contour
            largest_contour = max(rectangular_contours, key=lambda x: x[1])[0]
        
        # Create mask for the selected contour
        selected_mask = np.zeros_like(gray)
        cv2.drawContours(selected_mask, [largest_contour], -1, 255, -1)
        
        # Extract the region
        result = cv2.bitwise_and(self.processed_image, self.processed_image, mask=selected_mask)
        
        self.processed_image = result
        return result
    
    def center_region(self) -> np.ndarray:
        """
        Center the largest region in the image.
        
        Returns:
            np.ndarray: Image with centered region
        """
        if self.processed_image is None:
            raise ValueError("No image loaded. Use load_image() first.")
        
        # Convert to grayscale for contour detection
        gray = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return self.processed_image
        
        # Find largest contour and its bounding box
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Crop the region
        cropped = self.processed_image[y:y+h, x:x+w]
        
        # Create centered image
        H, W = self.original_image.shape[:2]
        centered = np.zeros_like(self.original_image)
        start_x = (W - w) // 2
        start_y = (H - h) // 2
        
        # Ensure the cropped region fits within bounds
        end_y = min(start_y + h, H)
        end_x = min(start_x + w, W)
        crop_h = end_y - start_y
        crop_w = end_x - start_x
        
        centered[start_y:end_y, start_x:end_x] = cropped[:crop_h, :crop_w]
        
        self.processed_image = centered
        return centered
    
    def add_transparency(self, black_color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
        """
        Add transparency to the image by making specified color transparent.
        
        Args:
            black_color (tuple): RGB color to make transparent
            
        Returns:
            np.ndarray: Image with alpha channel
        """
        if self.processed_image is None:
            raise ValueError("No image loaded. Use load_image() first.")
        
        # Create mask where specified color pixels are 0, others are 255
        mask = np.where((self.processed_image == black_color).all(axis=2), 0, 255).astype(np.uint8)
        
        # Convert to BGRA
        img_bgra = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2BGRA)
        
        # Set alpha channel
        img_bgra[:, :, 3] = mask
        
        self.processed_image = img_bgra
        return img_bgra
    
    def detect_rotation_angle(self, canny_low: int = 50, canny_high: int = 150, 
                            hough_threshold: int = 200) -> float:
        """
        Detect the rotation angle of the image using Hough line detection.
        
        Args:
            canny_low (int): Lower threshold for Canny edge detection
            canny_high (int): Upper threshold for Canny edge detection
            hough_threshold (int): Threshold for Hough line detection
            
        Returns:
            float: Median rotation angle in degrees
        """
        if self.processed_image is None:
            raise ValueError("No image loaded. Use load_image() first.")
        
        # Convert to grayscale
        if len(self.processed_image.shape) == 3:
            gray = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.processed_image
        
        # Edge detection
        edges = cv2.Canny(gray, canny_low, canny_high, apertureSize=3)
        
        # Hough line detection
        lines = cv2.HoughLines(edges, 1, np.pi / 180, hough_threshold)
        
        if lines is None:
            return 0.0
        
        # Calculate angles
        angles = []
        for line in lines:
            for rho, theta in line:
                angle = np.rad2deg(theta)
                # Adjust angle to be between -90 and 90
                if angle > 90:
                    angle -= 180
                angles.append(angle)
        
        return np.median(angles) if angles else 0.0
    
    def rotate_image(self, angle: Optional[float] = None, 
                    border_mode: int = cv2.BORDER_REPLICATE) -> np.ndarray:
        """
        Rotate the image by the specified angle or auto-detected angle.
        
        Args:
            angle (float, optional): Rotation angle in degrees. If None, auto-detect.
            border_mode (int): Border mode for rotation
            
        Returns:
            np.ndarray: Rotated image
        """
        if self.processed_image is None:
            raise ValueError("No image loaded. Use load_image() first.")
        
        if angle is None:
            angle = self.detect_rotation_angle()
        
        # Get image dimensions and center
        h, w = self.processed_image.shape[:2]
        center = (w // 2, h // 2)
        
        # Create rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Rotate image
        rotated = cv2.warpAffine(self.processed_image, M, (w, h), 
                               flags=cv2.INTER_LINEAR, borderMode=border_mode)
        
        self.processed_image = rotated
        return rotated
    
    def save_image(self, output_path: str) -> None:
        """
        Save the processed image to file.
        
        Args:
            output_path (str): Output file path
        """
        if self.processed_image is None:
            raise ValueError("No processed image to save.")
        
        cv2.imwrite(output_path, self.processed_image)
    
    def reset_to_original(self) -> None:
        """Reset the processed image to the original image."""
        if self.original_image is None:
            raise ValueError("No original image loaded.")
        
        self.processed_image = self.original_image.copy()
    
    def crop_to_content_bounds(self, padding: int = 10) -> np.ndarray:
        """
        Crop the image to the actual content bounds with optional padding.
        
        Args:
            padding (int): Padding around the content in pixels
            
        Returns:
            np.ndarray: Cropped image
        """
        if self.processed_image is None:
            raise ValueError("No image loaded. Use load_image() first.")
        
        # Convert to grayscale to find content bounds
        if len(self.processed_image.shape) == 3:
            gray = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.processed_image
        
        # Find all non-zero pixels (content)
        coords = cv2.findNonZero(gray)
        
        if coords is not None:
            # Get bounding rectangle of all content
            x, y, w, h = cv2.boundingRect(coords)
            
            # Add padding
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(self.processed_image.shape[1] - x, w + 2 * padding)
            h = min(self.processed_image.shape[0] - y, h + 2 * padding)
            
            # Crop the image
            cropped = self.processed_image[y:y+h, x:x+w]
            self.processed_image = cropped
            
            return cropped
        
        return self.processed_image
        """
        Get the current processed image.
        
        Returns:
            np.ndarray: Current processed image
        """
        return self.processed_image
    
    def process_fabric_pipeline(self, image_path: str, output_path: str, 
                              add_transparency: bool = True, 
                              auto_rotate: bool = True,
                              crop_to_bounds: bool = True) -> None:
        """
        Complete processing pipeline specifically for fabric/textile images.
        
        Args:
            image_path (str): Input image path
            output_path (str): Output image path
            add_transparency (bool): Whether to add transparency
            auto_rotate (bool): Whether to auto-rotate based on detected lines
            crop_to_bounds (bool): Whether to crop to content bounds
        """
        # Load and process
        self.load_image(image_path)
        
        # Extract rectangular region (better for fabrics)
        self.extract_rectangular_region()
        
        # Crop to actual content bounds
        if crop_to_bounds:
            self.crop_to_content_bounds()
        
        # Center the region if needed
        if not crop_to_bounds:
            self.center_region()
        
        if add_transparency:
            self.add_transparency()
        
        if auto_rotate:
            self.rotate_image()
        
        # Save result
        self.save_image(output_path)


# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = ImageProcessor()
    
    # Method 1: Use the fabric-specific pipeline (recommended for your use case)
    processor.process_fabric_pipeline('backend/border_rotated.png', 'cleaned_fabric.png')
    
    # Method 2: Step by step processing for fabric
    processor.load_image('backend/border_rotated.png')
    
    # Extract only rectangular regions (filters out triangular parts)
    processor.extract_rectangular_region(threshold=10, aspect_ratio_filter=True)
    
    # Crop to actual content bounds (removes extra black space)
    processor.crop_to_content_bounds(padding=5)
    
    # Add transparency to black areas
    processor.add_transparency()
    
    # Auto-rotate if needed
    angle = processor.detect_rotation_angle()
    if abs(angle) > 1:  # Only rotate if significant angle detected
        print(f"Detected rotation angle: {angle:.2f} degrees")
        processor.rotate_image(angle)
    
    # Save final result
    processor.save_image('final_fabric_result.png')
    
    # Method 3: Manual rectangular extraction with custom parameters
    processor.load_image('backend/border_rotated.png')
    
    # For very specific rectangular extraction
    processor.extract_rectangular_region(
        threshold=15,  # Higher threshold for cleaner edges
        aspect_ratio_filter=True  # Ensure width > height
    )
    
    processor.save_image('rectangular_only.png')