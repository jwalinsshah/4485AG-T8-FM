// index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS
import './styles.css'; // Import your custom CSS file
import DatabaseUpload from './components/DatabaseUpload';
import SchemaUpload from './components/SchemaUpload';
import AlertConfig from './components/AlertConfig';
import AlertsList from './components/AlertsList';
import { Container } from 'react-bootstrap'; // Import Bootstrap Container

function App() {
  return (
    <Container className="mt-4">
      <header className="text-center mb-4">
        <h1>Super Fault Management System</h1>
      </header>
      <DatabaseUpload />
      <SchemaUpload />
      <AlertConfig />
      <AlertsList />
    </Container>
  );
}

// Create a root
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the App component to the root
root.render(<App />);
