// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.3.1/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.3.1/firebase-analytics.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBvFlP36RfSafrYWGUcfZCevooJDmBxKMo",
  authDomain: "project-2af6e.firebaseapp.com",
  projectId: "project-2af6e",
  storageBucket: "project-2af6e.firebasestorage.app",
  messagingSenderId: "3802194154",
  appId: "1:3802194154:web:6b657e5b3d64e7beebb793",
  measurementId: "G-TREZ4H1W7W",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
