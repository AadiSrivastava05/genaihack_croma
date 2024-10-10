// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBk45b5SJVHoylMbLI7FIqlucJDVDLw7wI",
  authDomain: "croma-genai-ex.firebaseapp.com",
  projectId: "croma-genai-ex",
  storageBucket: "croma-genai-ex.appspot.com",
  messagingSenderId: "919360745289",
  appId: "1:919360745289:web:48ee9df6692dd9dcd37498"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
const auth = getAuth(app);

export { auth };