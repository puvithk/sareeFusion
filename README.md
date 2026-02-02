# SareeFusion

SareeFusion is an innovative AI-powered application designed to revolutionize Saree design. It allows users to upload individual saree components (Border, Pallu, Body), process them into vectors, and generate unique, high-quality Saree designs using advanced generative AI.

## 🚀 Features

*   **AI-Powered Design Generation**: Create unique saree designs by combining Border, Pallu, and Body elements using Google's Gemini AI.
*   **Component Management**: Upload and process individual saree parts (Border, Pallu, Body).
*   **Vectorization**: Automatically convert uploaded images into flat vector graphics for better design integration.
*   **Cloud Storage**: Secure media storage using AWS S3.
*   **Design History**: Browse and manage your generated designs, stored in MongoDB.
*   **Responsive UI**: A modern, responsive frontend built with React and Bootstrap.

## 🛠️ Tech Stack

### Frontend
*   **Framework**: [React](https://react.dev/)
*   **Build Tool**: [Vite](https://vitejs.dev/)
*   **Styling**: [Bootstrap](https://getbootstrap.com/), [React Bootstrap](https://react-bootstrap.netlify.app/)
*   **Carousel**: Owl Carousel
*   **Language**: JavaScript/JSX

### Backend
*   **Framework**: [Flask](https://flask.palletsprojects.com/) (Python)
*   **Database**: [MongoDB](https://www.mongodb.com/) (via Flask-PyMongo & MongoEngine)
*   **Cloud Storage**: [AWS S3](https://aws.amazon.com/s3/) (via Boto3)
*   **AI/ML**: 
    *   Google Gemini (GenAI)
    *   OpenCV (`cv2`) for image processing
    *   Pillow (`PIL`) for image manipulation
*   **Server**: Gunicorn

### Infrastructure
*   **Containerization**: Docker (Multi-stage build)

## 📋 Prerequisites

Ensure you have the following installed:
*   [Node.js](https://nodejs.org/) (v16+ recommended)
*   [Python](https://www.python.org/) (v3.10+)
*   [Docker](https://www.docker.com/) (optional, for containerized deployment)
*   [MongoDB Atlas](https://www.mongodb.com/atlas) account (or local MongoDB)
*   AWS Account with S3 Bucket
*   Google Cloud Account with Gemini API access

## ⚙️ Environment Variables

Create a `.env` file in the `backend` directory with the following keys:

```ini
GOOGLE_API_KEY=your_google_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=your_aws_region
MONGO_URI=your_mongodb_connection_string
```

> **Note**: For the frontend, you may need to configure API base URLs depending on your deployment.

## 🏃‍♂️ Getting Started (Local Development)

### Backend

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Run the Flask server:
    ```bash
    python main.py
    ```
    The backend will start on `http://localhost:5000`.

### Frontend

1.  Navigate to the frontend directory:
    ```bash
    cd Fusion-Saree-Frontend/saree-fusion-app
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Run the development server:
    ```bash
    npm run dev
    ```
    The frontend will start on the URL provided by Vite (typically `http://localhost:5173`).


## 📂 Project Structure

```
sareeFusion/
├── backend/                 # Python Flask Backend
│   ├── main.py              # Application Entry Point
│   ├── requirements.txt     # Python Dependencies
│   ├── Genereating/         # AI Generation Logic
│   ├── Proccessing/         # Image Processing Modules
│   └── models.py            # Database Models
├── Fusion-Saree-Frontend/   # React Frontend
│   └── saree-fusion-app/    # Source Code
│       ├── src/
│       ├── public/
│       └── package.json

```

## 🤝 Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## 📄 License

[MIT License](LICENSE)
