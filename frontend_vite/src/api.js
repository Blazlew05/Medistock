import axios from "axios";`nconst API = axios.create({ baseURL: "http://localhost:8000/api/", headers: { "Content-Type": "application/json" } });`nexport default API;
