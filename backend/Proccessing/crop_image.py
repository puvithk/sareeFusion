from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter1d, label
import cv2
class CropCenter:
    def crop_pre_region(self, img, width_cm=20, height_cm=6, dpi=72, save_path=None, show=True):
        """
        Crop a region of width_cm x height_cm (in cm) from the center of the image before further processing.
        Ensures the output is vertically aligned (height > width). If not, rotates by 90 degrees.
        """
        
        width_px = int(width_cm / 2.54 * dpi)
        height_px = int(height_cm / 2.54 * dpi)
        img_w, img_h = img.size

        # Center crop box
        left = max(0, (img_w - width_px) // 2)
        top = max(0, (img_h - height_px) // 2)
        right = min(img_w, left + width_px)
        bottom = min(img_h, top + height_px)

        cropped = img.crop((left, top, right, bottom))
        # Ensure vertical alignment: height > width
        if cropped.width <= cropped.height:
            cropped = cropped.rotate(90, expand=True)
        return cropped
    #Border 
    def crop_middle_border(self ,img, orientation='vertical', show_image=False, save_image=False, side_crop_percent=0.1, width_cm=15, height_cm=25, dpi=72):
        """
        Detect and crop the exact border region where it's most visible and prominent.
        Output is resized to width_cm x height_cm (in cm) at the specified dpi.
        """
        
        width, height = img.size
        img_np = np.array(img)

        if orientation == 'horizontal':
            border_scores = []
            for y in range(height):
                row = img_np[y, :, :]
                row_variance = np.var(row)
                row_gray = np.mean(row, axis=1)
                edges = np.abs(np.diff(row_gray))
                edge_density = np.mean(edges)
                color_diversity = np.std(row)
                border_score = row_variance * edge_density * color_diversity
                border_scores.append(border_score)
            border_scores = np.array(border_scores)
            smoothed_scores = gaussian_filter1d(border_scores, sigma=5)
            threshold = np.percentile(smoothed_scores, 85)
            border_mask = smoothed_scores > threshold
            labeled_array, num_features = label(border_mask)
            if num_features == 0:
                border_thickness = int(0.1 * height)
                y_min, y_max = 0, border_thickness
            else:
                largest_region = 0
                max_size = 0
                for i in range(1, num_features + 1):
                    region_size = np.sum(labeled_array == i)
                    if region_size > max_size:
                        max_size = region_size
                        largest_region = i
                border_coords = np.where(labeled_array == largest_region)[0]
                y_min, y_max = border_coords.min(), border_coords.max() + 1
            border_region = img_np[y_min:y_max, :, :]
            detected_orientation = 'horizontal'
        elif orientation == 'vertical':
            border_scores = []
            for x in range(width):
                col = img_np[:, x, :]
                col_variance = np.var(col)
                col_gray = np.mean(col, axis=1)
                edges = np.abs(np.diff(col_gray))
                edge_density = np.mean(edges)
                color_diversity = np.std(col)
                border_score = col_variance * edge_density * color_diversity
                border_scores.append(border_score)
            border_scores = np.array(border_scores)
            smoothed_scores = gaussian_filter1d(border_scores, sigma=5)
            threshold = np.percentile(smoothed_scores, 85)
            border_mask = smoothed_scores > threshold
            labeled_array, num_features = label(border_mask)
            if num_features == 0:
                border_thickness = int(0.1 * width)
                x_min, x_max = 0, border_thickness
            else:
                largest_region = 0
                max_size = 0
                for i in range(1, num_features + 1):
                    region_size = np.sum(labeled_array == i)
                    if region_size > max_size:
                        max_size = region_size
                        largest_region = i
                border_coords = np.where(labeled_array == largest_region)[0]
                x_min, x_max = border_coords.min(), border_coords.max() + 1
            border_region = img_np[:, x_min:x_max, :]
            detected_orientation = 'vertical'
        else:
            raise ValueError("Orientation must be 'horizontal' or 'vertical'.")

        # Remove black/white/very dark background
        black_threshold = 30
        mask = ~(
            (border_region == [0, 0, 0]).all(axis=-1) | 
            (border_region == [255, 255, 255]).all(axis=-1) |
            ((border_region < black_threshold).all(axis=-1))
        )
        coords = np.argwhere(mask)
        if coords.size == 0:
            print("No visible border found.")
            return
        y_min_local, x_min_local = coords.min(axis=0)
        y_max_local, x_max_local = coords.max(axis=0) + 1
        current_width = x_max_local - x_min_local
        side_crop_pixels = int(current_width * side_crop_percent)
        x_min_local += side_crop_pixels
        x_max_local -= side_crop_pixels
        if x_min_local >= x_max_local:
            x_min_local = x_min_local - side_crop_pixels
            x_max_local = x_max_local + side_crop_pixels
        if orientation == 'horizontal':
            crop_box = (x_min_local, y_min + y_min_local, x_max_local, y_min + y_max_local)
        else:
            crop_box = (x_min + x_min_local, y_min_local, x_min + x_max_local, y_max_local)
        cropped_img = img.crop(crop_box)
        if detected_orientation == 'horizontal':
            cropped_img = cropped_img.rotate(90, expand=True)
            print(f"Rotated horizontal border to vertical orientation")
        # Resize to cm size at dpi
        width_px = int(width_cm / 2.54 * dpi)
        height_px = int(height_cm / 2.54 * dpi)
        # Only resize if the crop is larger than the target size (downscale only)
        if cropped_img.width > width_px or cropped_img.height > height_px:
            cropped_img = cropped_img.resize((width_px, height_px), Image.Resampling.LANCZOS)
            print(f"Downscaled border to {width_px}x{height_px} pixels ({width_cm}x{height_cm} cm at {dpi} DPI)")
        else:
            print(f"Output kept at cropped size: {cropped_img.size} (no upscaling, so no blur)")
        if show_image:
            cropped_img.show()
        if save_image:
            cropped_img.save("border_clean_cropped.png")
        return cropped_img

    #Body ,  Pallu 
    def crop_middle_image(self ,img, show_image=False, save_image=False):
        """
        Crop the central 50% area of the entire image (for pallu/body/etc).
        """
       
        width, height = img.size
        left = width * 0.25
        top = height * 0.25
        right = width * 0.75
        bottom = height * 0.75
        cropped = img.crop((left, top, right, bottom))
        if show_image:
            cropped.show()
        if save_image:
            cropped.save("middle_image_crop.png")
        return cropped

# Example usage
if __name__ == "__main__":
    # Now you can call crop_pre_region here!
    crop_center = CropCenter()
    img = Image.open("backend\Proccessing\WhatsApp Image 2025-06-20 at 13.20.57_8b0ee245.jpg")
    pre_cropped = crop_center.crop_pre_region(
        img,
        width_cm=20,
        height_cm=4.5,
        dpi=72,
        save_path="pre_cropped.png",
        show=True
    )

    # # Then, pass the pre-cropped image to your border function
    pre_cropped.save("temp_input.png")  # Save to disk for compatibility
    # border_crop = crop_center.crop_middle_border(
    #     "temp_input.png",
    #     orientation="vertical",
    #     side_crop_percent=0.1,
    #     width_cm=22,      # or whatever you want for the final output
    #     height_cm=4.5,
    #     dpi=72,
    #     show_image=False,
    #     save_image=False
    # )

    # body_crop = crop_center.crop_middle_image("D:/Belur project/saree_fusion/test_image/body.jpg", show_image=False, save_image=False)

    # # Show only the two outputs
    # if border_crop:
    #     border_crop.show()
    #     border_crop.save("final_cropped_border.png")

    # if body_crop:
    #     body_crop.show()
    #     body_crop.save("final_cropped_body.png")

