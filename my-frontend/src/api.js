import axios from 'axios';
import { API_BASE_URL } from './config';
import { useAuth0 } from '@auth0/auth0-react';

export const useApi = () => {
  const { getAccessTokenSilently } = useAuth0();

  const fetchData = async (endpoint) => {
    const token = await getAccessTokenSilently();
    const response = await axios.get(`${API_BASE_URL}/${endpoint}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  };

  return { fetchData };
};
