import React from 'react';
import ReactDOM from 'react-dom/client';
import { Auth0Provider } from '@auth0/auth0-react';
import App from './App'; // Make sure to import your main App component

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <Auth0Provider
    domain="dev-ysm1cgla8nxn27sn.us.auth0.com"
    clientId="RsLyXSd4XjUMY7bhYVo7SzzMCTfUZKDt"
    redirectUri={window.location.origin} // Redirect to the root URL after login
    audience="YOUR_API_IDENTIFIER" // Optional: add your API identifier if needed
  >
    <App />
  </Auth0Provider>
);
