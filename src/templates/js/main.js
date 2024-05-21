import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.1/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.12.1/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyAWhxa21SdGN-THuU-hRpBEZN2SBhiXMx4",
    authDomain: "achc-abe85.firebaseapp.com",
    projectId: "achc-abe85",
    storageBucket: "achc-abe85.appspot.com",
    messagingSenderId: "487916204900",
    appId: "1:487916204900:web:2665e5864af81cc7cbc071",
    measurementId: "G-341JJQSJ7Y"
  };

// Initialize Firebase
const app = initializeApp(firebaseConfig);

const auth = getAuth();
auth.languageCode = 'en';

const provider = new GoogleAuthProvider();

const googleLogin = document.getElementById("google");
googleLogin.addEventListener("click", function () {
    signInWithPopup(auth, provider)
        .then((result) => {
            const user = result.user;
            console.log(user);

            fetch('/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: user.email })
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    console.error('Error: Unable to redirect');
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }).catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;
            console.error('Error during sign-in:', errorMessage);
        });
});