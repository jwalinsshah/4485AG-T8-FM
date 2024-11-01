// App.js
import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import DatabaseUpload from './components/DatabaseUpload';
import SchemaUpload from './components/SchemaUpload';
import AlertConfig from './components/AlertConfig';
import AlertsList from './components/AlertsList';
import { Container, Button } from 'react-bootstrap';

function App() {
  const { loginWithRedirect, logout, isAuthenticated, user } = useAuth0();

  return (
    <Container className="mt-4 text-center">
      <header className="mb-4">
        <h1>Super Fault Management System</h1>
      </header>
      {!isAuthenticated ? (
        <div>
          <h2>Welcome! Please log in to access the system.</h2>
          <Button onClick={() => loginWithRedirect()} variant="primary">
            Log In
          </Button>
        </div>
      ) : (
        <div>
          <h2>Welcome, {user.name}</h2>
          <Button
            onClick={() => logout({ returnTo: window.location.origin })}
            variant="secondary"
            className="mb-4"
          >
            Log Out
          </Button>
          <DatabaseUpload />
          <SchemaUpload />
          <AlertConfig />
          <AlertsList />
        </div>
      )}
    </Container>
  );
}

export default App;
