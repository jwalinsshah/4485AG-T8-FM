import React, { useEffect, useState, useCallback } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

function App() {
  const { loginWithRedirect, logout, isAuthenticated, user, getAccessTokenSilently } = useAuth0();
  const [message, setMessage] = useState('');

  // Use useCallback to memoize the fetch function
  const fetchRestrictedData = useCallback(async () => {
    if (!isAuthenticated) return; // Ensure user is authenticated
    
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch('http://127.0.0.1:8000/restricted', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setMessage(data.message);
    } catch (error) {
      console.error('Error fetching restricted data:', error);
      setMessage('Failed to fetch restricted data');
    }
  }, [getAccessTokenSilently, isAuthenticated]); // Add dependencies here

  useEffect(() => {
    fetchRestrictedData();
  }, [fetchRestrictedData]); // Include fetchRestrictedData as a dependency

  return (
    <div className="App">
      <h1>React with FastAPI and Auth0</h1>

      {isAuthenticated ? (
        <>
          <p>Welcome, {user.name}!</p>
          <button onClick={() => logout({ returnTo: window.location.origin })}>Log out</button>
          <h2>Restricted Message:</h2>
          <p>{message}</p>
        </>
      ) : (
        <button onClick={() => loginWithRedirect()}>Log in</button>
      )}
      
      {/* Optional: Display Schema Data and Alerts */}
      {/* Currently commented out to avoid ESLint warnings */}
      {/* <h2>Schema Data</h2>
      <pre>{JSON.stringify(schemaData, null, 2)}</pre>

      <h2>Alerts</h2>
      <pre>{JSON.stringify(alerts, null, 2)}</pre> */}
    </div>
  );
}

export default App;
