import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { Auth0Provider } from '@auth0/auth0-react';
import YourComponent from './YourComponent'; // Replace with your actual component path
import Callback from './callback'; // Ensure the casing matches

const domain = "dev-ek2dti7hmslc8nga.us.auth0.com";
const clientId = "HYU43Nk[XA0xib7V5EsPlE3dT73RLQ3i"; // Ensure this is your actual client ID
const audience = "cs4485"; // Your API audience
const redirectUri = "http://localhost:3000/callback"; // Your callback URL

const App = () => {
  return (
    <Router>
      <Auth0Provider 
        domain={domain} 
        clientId={clientId} 
        authorizationParams={{
          redirect_uri: redirectUri,
          audience: audience,
        }}
      >
        <Switch>
          <Route path="/callback" component={Callback} /> {/* Route for the Auth0 callback */}
          <Route path="/" component={YourComponent} /> {/* Default route */}
          {/* Add more routes here as needed */}
        </Switch>
      </Auth0Provider>
    </Router>
  );
};

export default App;

