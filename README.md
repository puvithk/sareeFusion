# SareeFusion

SareeFusion is a web application for uploading, processing, and generating saree images using advanced image segmentation and processing models. The project consists of a Flask backend and a React frontend built with Vite.

## Features
- Upload saree images (body, pallu, pattern)
- Automatic image segmentation and part extraction
- Generate saree templates and final images
- Browse and download uploaded/generated images

## Folder Structure
```
sareeFusion/
├── backend/         # Flask backend (API, image processing, storage)
├── sareefusion/     # Frontend (React + Vite app)
├── .gitignore
├── .gitattributes
└── README.md        # Project documentation (this file)
```

## Backend Setup (Flask)
1. **Navigate to backend:**
   ```sh
   cd sareeFusion/backend
   ```
2. **Create a virtual environment (recommended):**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   - Create a `.env` file if not present. Example:
     ```env
     FLASK_ENV=development
     SECRET_KEY=your_secret_key
     ```
5. **Run the backend server:**
   ```sh
   python app.py
   ```
   The server will start on `http://0.0.0.0:5000` by default.

## Frontend Setup (React + Vite)
1. **Navigate to the frontend directory:**
   ```sh
   cd sareeFusion/sareefusion
   ```
2. **Install dependencies:**
   ```sh
   npm install
   # or
   yarn install
   ```
3. **Start the frontend development server:**
   ```sh
   npm run dev
   # or
   yarn dev
   ```
   The app will typically run on `http://localhost:5173` (Vite default).

> **Note:** If you want to build for production, use:
> ```sh
> npm run build
> # or
> yarn build
> ```
> The output will be in the `dist/` folder.

## API Endpoints (Backend)
- `POST /process-image` — Upload and process an image, extracting parts
- `POST /upload-pallu`, `/upload-body`, `/upload-pattern` — Upload saree parts
- `POST /generate` — Generate a saree using uploaded parts
- `GET /images` — List all uploaded images
- `GET /image/<filename>` — Download a specific uploaded image

## Example API Usage
**Upload an image:**
```sh
curl -F "image=@yourfile.png" http://localhost:5000/process-image
```

**Generate a saree:**
```sh
curl -X POST -H "Content-Type: application/json" \
  -d '{"border": "<border_id>", "pallu": "<pallu_id>", "pattern": "<pattern_id>", "body": "<body_id>"}' \
  http://localhost:5000/generate
```

## Contribution
- Pull requests are welcome!
- Please ensure code is well-documented and tested.

## Notes
- The `uploads/` and `upload_parts/` folders in the backend are ignored by git and used for temporary storage.
- Make sure required model files are present in the `backend/Models/` directory.
- For any issues, please open an issue or contact the maintainer. 