import React from 'react';
import { Auth0Provider } from '@auth0/auth0-react';

const Auth0ProviderWithHistory = ({ children }) => {
    const domain = "dev-ek2dti7hmslc8nga.us.auth0.com";
    const clientId = "HYU43Nk[XA0xib7V5EsPlE3dT73RLQ3i"; // Ensure this is your actual client ID
    const audience = "cs4485";
    const redirectUri = window.location.origin + "/callback"; // Adjust as needed

    return (
        <Auth0Provider
            domain={domain}
            clientId={clientId}
            authorizationParams={{
                redirect_uri: redirectUri,
                audience: audience,
            }}
        >
            {children}
        </Auth0Provider>
    );
};

export default Auth0ProviderWithHistory;
