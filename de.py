import streamlit as st
import requests
from PIL import Image, ImageDraw
import io

# Hugging Face Inference API details
API_URL = "https://api-inference.huggingface.co/models/facebook/detr-resnet-50"
headers = {"Authorization": "Bearer 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"}

# Function to query the model
def query(image_data):
    response = requests.post(API_URL, headers=headers, data=image_data)
    return response.json()

# Function to draw bounding boxes on the image
def draw_boxes(image, boxes):
    draw = ImageDraw.Draw(image)
    for box in boxes:
        coords = box['box']
        xmin = coords['xmin']
        ymin = coords['ymin']
        xmax = coords['xmax']
        ymax = coords['ymax']

        # Draw bounding box
        draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=3)

        # Draw label with background
        label = f"{box['label']} ({box['score']:.2f})"
        # Get text size using textbbox
        text_bbox = draw.textbbox((xmin, ymin), label)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Draw background for the label
        draw.rectangle([xmin, ymin - text_height, xmin + text_width, ymin], fill="red")
        draw.text((xmin, ymin - text_height), label, fill="white")

    return image


# Streamlit UI
st.set_page_config(page_title="Object Detection App", layout="wide")

# Header
st.title("🔍 Object Detection with Hugging Face")
st.write("This app uses the **DETR-ResNet-50** model to detect objects in an image. Upload an image and see the detected objects with bounding boxes.")

# Sidebar for file upload
st.sidebar.header("Upload Image")
uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Main content area
if uploaded_file is not None:
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("Original Image")
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)

    # Convert image to bytes and send to API
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes = image_bytes.getvalue()

    # Query the model
    output = query(image_bytes)

    with col2:
        if isinstance(output, list):
            st.subheader("Detected Objects")
            # Draw boxes on the image
            image_with_boxes = draw_boxes(image, output)
            # Display the image with bounding boxes
            st.image(image_with_boxes, caption='Image with Detected Objects', use_column_width=True)
        else:
            st.error("Unexpected API response format.")
            st.json(output)  # Display the raw JSON for debugging

    # Optionally display detection results
    if isinstance(output, list):
        st.sidebar.subheader("Detected Objects")
        for obj in output:
            st.sidebar.write(f"- **{obj['label']}** with confidence {obj['score']:.2f}")
else:
    st.info("Please upload an image to get started.")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Developed by Tanmay and Sunny")
