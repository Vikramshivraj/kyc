import { useState } from "react";
import {
  loginUser,
  registerUser,
  getCurrentUser,
  uploadDocument,
  getMyDocuments,
} from "./services/api";

function App() {
  const [mode, setMode] = useState("login");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [message, setMessage] = useState("");
  const [user, setUser] = useState(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");

  const [documents, setDocuments] = useState([]);

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");

    try {
      if (mode === "register") {
        await registerUser(email, password);

        setMessage("Registration successful. You can now login.");
        setMode("login");
        setPassword("");

        return;
      }

      const data = await loginUser(email, password);

      localStorage.setItem("access_token", data.access_token);

      const userData = await getCurrentUser(data.user_id);
      
      setUser(userData);

      const documentData = await getMyDocuments();

      setDocuments(documentData);

      setMessage("Login successful!");
    } catch (error) {
      setMessage(error.message);
    }
  }

function handleLogout() {
  localStorage.removeItem("access_token");

  setUser(null);
  setDocuments([]);
  setSelectedFile(null);

  setMessage("Logged out successfully.");
}

async function handleUpload() {
  if (!selectedFile) {
    setUploadMessage("Please select a file first.");
    return;
  }

  setUploadMessage("");

  try {
    const data = await uploadDocument(selectedFile);

setUploadMessage(
  `Upload successful. Document ID: ${data.id}`
);

setSelectedFile(null);

const documentData = await getMyDocuments();

setDocuments(documentData);
  } catch (error) {
    setUploadMessage(error.message);
  }
}

  return (
    <div>
      <h1>KYC Verification Platform</h1>

      <h2>{mode === "login" ? "Login" : "Register"}</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Email</label>
          <br />

          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>

        <br />

        <div>
          <label>Password</label>
          <br />

          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </div>

        <br />

        <button type="submit">
          {mode === "login" ? "Login" : "Register"}
        </button>
      </form>

      <br />

      <button
        type="button"
        onClick={() => {
          setMode(mode === "login" ? "register" : "login");
          setMessage("");
        }}
      >
        {mode === "login"
          ? "Create a new account"
          : "Already have an account? Login"}
      </button>

      {message && <p>{message}</p>}
      {user && (
  <div>
    <hr />

    <h2>Upload KYC Document</h2>

    <input
      type="file"
      accept=".pdf,.png,.jpg,.jpeg"
      onChange={(event) => {
        setSelectedFile(event.target.files[0]);
        setUploadMessage("");
      }}
    />

    <br />
    <br />

    <button type="button" onClick={handleUpload}>
      Upload Document
    </button>

    {uploadMessage && <p>{uploadMessage}</p>}
  </div>
)}
{user && (
  <div>
    <hr />

    <h2>My Documents</h2>

    {documents.length === 0 ? (
      <p>No documents uploaded yet.</p>
    ) : (
      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>ID</th>
            <th>Filename</th>
            <th>Type</th>
            <th>Size</th>
            <th>Status</th>
            <th>Uploaded</th>
          </tr>
        </thead>

        <tbody>
          {documents.map((document) => (
            <tr key={document.id}>
              <td>{document.id}</td>
              <td>{document.original_filename}</td>
              <td>{document.content_type}</td>
              <td>{document.file_size} bytes</td>
              <td>{document.status}</td>
              <td>
                {new Date(document.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </div>
)}
      {user && (
  <button type="button" onClick={handleLogout}>
    Logout
  </button>
      )}
      
      {user && (
        <div>
          <h3>Logged in user</h3>

          <p>ID: {user.id}</p>

          <p>Email: {user.email}</p>

          <p>Role: {user.role}</p>
        </div>
    )}
    </div>
    
  );
}

export default App;