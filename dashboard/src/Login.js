import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from './firebase';
import { createUserWithEmailAndPassword, signInWithEmailAndPassword, updateProfile } from 'firebase/auth';
import './Login.css';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [error, setError] = useState('');
    const [isCreatingAccount, setIsCreatingAccount] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        document.body.classList.add('login-page');
        return () => {
            document.body.classList.remove('login-page');
        };
    }, []);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await signInWithEmailAndPassword(auth, email, password);
            navigate('/home');
        } catch (error) {
            console.error('Login error:', error);
            if (error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password') {
                setError('Invalid email or password. Please try again.');
            } else if (error.code === 'auth/invalid-email') {
                setError('Invalid email format. Please enter a valid email.');
            } else {
                setError('An error occurred during login. Please try again.');
            }
        }
    };

    const handleCreateAccount = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            await updateProfile(userCredential.user, { displayName: name });
            navigate('/home');
        } catch (error) {
            console.error('Account creation error:', error);
            if (error.code === 'auth/email-already-in-use') {
                setError('This email is already in use. Please use a different email or try logging in.');
            } else if (error.code === 'auth/weak-password') {
                setError('Password is too weak. Please use a stronger password.');
            } else if (error.code === 'auth/invalid-email') {
                setError('Invalid email format. Please enter a valid email.');
            } else {
                setError('An error occurred during account creation. Please try again.');
            }
        }
    };

    return (
        <div className='login-wrapper'>
            <div className="body-login">
                <div className="login-container">
                    <div className="login-box">
                        {/* <img src={logo} alt="Logo" className="logo" /> */}
                        <h2>Login</h2>
                        <p></p>
                        {isCreatingAccount ? (
                            <form onSubmit={handleCreateAccount}>
                                <div className="input-group">
                                    <input
                                        type="text"
                                        placeholder="Name"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="input-group">
                                    <input
                                        type="email"
                                        placeholder="Email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="input-group">
                                    <input
                                        type="password"
                                        placeholder="Password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>
                                <button type="submit" className="login-button">CREATE ACCOUNT</button>
                                {error && <p className="error-message">{error}</p>}
                                <p>Already have an account? <a href="#" onClick={() => setIsCreatingAccount(false)} className="login-link">Sign in.</a></p>
                            </form>
                        ) : (
                            <form onSubmit={handleLogin}>
                                <div className="input-group">
                                    <input
                                        type="email"
                                        placeholder="Email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="input-group">
                                    <input
                                        type="password"
                                        placeholder="Password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="remember-me">
                                    <input type="checkbox" id="remember-me" />
                                    <label htmlFor="remember-me">Remember me</label>
                                    <a href="/forgot-password" className="forgot-password-link"> Forgot Password?</a>
                                </div>
                                <button type="submit" className="login-button">SIGN IN</button>
                                {error && <p className="error-message">{error}</p>}
                                <p>Don't have an account? <a href="#" onClick={() => setIsCreatingAccount(true)} className="create-account-link">Create account.</a></p>
                            </form>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;