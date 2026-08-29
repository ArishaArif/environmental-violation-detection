import re
from fast_plate_ocr import LicensePlateRecognizer

# Initialize the global OCR model once so it does not reload on every frame
ocr_recognizer = LicensePlateRecognizer("cct-s-v2-global-model")

def validate_pakistani_plate(plate_text):
    if not plate_text:
        return False
    pattern = r"^[A-Z]{2,3}[-\s]?\d{3,4}$"
    return bool(re.match(pattern, plate_text.strip().upper()))

def extract_plate_data(crop_img):
    # Fail gracefully for completely empty or missing crops
    if crop_img is None or crop_img.size == 0:
        return {"plate_number": None, "plate_confidence": None}
        
    try:
        # Run OCR with return_confidence enabled
        ocr_result = ocr_recognizer.run(crop_img, return_confidence=True)
        
        if not ocr_result:
            return {"plate_number": None, "plate_confidence": None}
            
        raw_plate_obj = ocr_result[0] if isinstance(ocr_result, list) else ocr_result
        raw_plate = raw_plate_obj.plate
        
        # Extract mean character probability to un-mock the confidence score
        if hasattr(raw_plate_obj, 'char_probs') and raw_plate_obj.char_probs is not None:
            plate_conf = round(float(raw_plate_obj.char_probs.mean()), 2)
        else:
            plate_conf = None  # Changed from 0.0 to ensure strict null JSON translation
            
        # Clean and validate against standard regex
        clean_plate = raw_plate.upper().replace(" ", "-")
        is_valid = validate_pakistani_plate(clean_plate)
        
        # Return nulls if the plate fails validation
        if not is_valid:
            return {"plate_number": None, "plate_confidence": None}
            
        # Strictly match the backend schema (no 'is_valid' or 'review_status')
        return {
            "plate_number": clean_plate,
            "plate_confidence": plate_conf
        }
        
    except Exception as e:
        # Prevent the main CV pipeline from crashing on bad frames
        print(f"OCR Error Handled: {e}")
        return {"plate_number": None, "plate_confidence": None}