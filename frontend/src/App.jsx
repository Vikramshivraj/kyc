import { useState } from "react";

import {
  loginUser,
  registerUser,
  getCurrentUser,
  uploadDocument,
  getMyDocuments,
  getDocumentResult,
} from "./services/api";


function App() {
  // =========================================================
  // AUTH STATE
  // =========================================================

  const [mode, setMode] = useState("login");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [message, setMessage] = useState("");
  const [user, setUser] = useState(null);


  // =========================================================
  // DOCUMENT UPLOAD STATE
  // =========================================================

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");


  // =========================================================
  // DOCUMENT LIST STATE
  // =========================================================

  const [documents, setDocuments] = useState([]);


  // =========================================================
  // RESULT STATE
  // =========================================================

  const [selectedResult, setSelectedResult] = useState(null);
  const [resultLoading, setResultLoading] = useState(false);


  // =========================================================
  // LOGIN / REGISTER
  // =========================================================

  async function handleSubmit(event) {
    event.preventDefault();

    setMessage("");

    try {
      // -----------------------------------------------------
      // REGISTER
      // -----------------------------------------------------

      if (mode === "register") {
        await registerUser(email, password);

        setMessage(
          "Registration successful. You can now login."
        );

        setMode("login");
        setPassword("");

        return;
      }


      // -----------------------------------------------------
      // LOGIN
      // -----------------------------------------------------

      const data = await loginUser(email, password);

      localStorage.setItem(
        "access_token",
        data.access_token
      );


      // Get logged-in user
      const userData = await getCurrentUser(data.user_id);

      setUser(userData);


      // Get user's documents
      const documentData = await getMyDocuments();

      setDocuments(documentData);


      // Clear old result from previous session
      setSelectedResult(null);

      setMessage("Login successful!");

    } catch (error) {
      setMessage(error.message);
    }
  }


  // =========================================================
  // LOGOUT
  // =========================================================

  function handleLogout() {
    // Remove JWT
    localStorage.removeItem("access_token");


    // Clear user/session data
    setUser(null);


    // Clear documents
    setDocuments([]);


    // Clear selected upload file
    setSelectedFile(null);


    // Clear upload message
    setUploadMessage("");


    // VERY IMPORTANT:
    // Clear previously displayed verification result
    setSelectedResult(null);


    // Clear result loading state
    setResultLoading(false);


    // Clear login/register message
    setMessage("");


    // Reset login form
    setEmail("");
    setPassword("");


    // Go back to login mode
    setMode("login");
  }


  // =========================================================
  // DOCUMENT UPLOAD
  // =========================================================

  async function handleUpload() {
    if (!selectedFile) {
      setUploadMessage("Please select a file first.");
      return;
    }

    setUploadMessage("");

    // Clear previous result when uploading a new document
    setSelectedResult(null);

    try {
      const data = await uploadDocument(selectedFile);


      // Show successful upload message
      setUploadMessage(
        `Upload successful. Document ID: ${data.id}`
      );


      // Clear selected file
      setSelectedFile(null);


      // Refresh document list
      const documentData = await getMyDocuments();

      setDocuments(documentData);

    } catch (error) {
      setUploadMessage(error.message);
    }
  }


  // =========================================================
  // CHECK DOCUMENT RESULT
  // =========================================================

  async function checkResult(documentId) {
    try {
      setResultLoading(true);

      // Remove previously displayed result
      setSelectedResult(null);


      // Fetch result from backend
      const result = await getDocumentResult(documentId);

      console.log("Document result:", result);


      // Display result
      setSelectedResult(result);

    } catch (error) {
      console.error("Result fetch error:", error);

      alert(error.message);

    } finally {
      setResultLoading(false);
    }
  }


  // =========================================================
  // UI
  // =========================================================

  return (
    <div>

      {/* =====================================================
          APPLICATION TITLE
      ====================================================== */}

      <h1>KYC Verification Platform</h1>


      {/* =====================================================
          LOGIN / REGISTER SECTION
      ====================================================== */}

      {!user && (
        <>
          <h2>
            {mode === "login" ? "Login" : "Register"}
          </h2>


          <form onSubmit={handleSubmit}>

            {/* EMAIL */}

            <div>
              <label>Email</label>
              <br />

              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                required
              />
            </div>


            <br />


            {/* PASSWORD */}

            <div>
              <label>Password</label>
              <br />

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                required
              />
            </div>


            <br />


            {/* SUBMIT */}

            <button type="submit">
              {mode === "login"
                ? "Login"
                : "Register"}
            </button>

          </form>


          <br />


          {/* LOGIN / REGISTER TOGGLE */}

          <button
            type="button"
            onClick={() => {
              setMode(
                mode === "login"
                  ? "register"
                  : "login"
              );

              setMessage("");
            }}
          >
            {mode === "login"
              ? "Create a new account"
              : "Already have an account? Login"}
          </button>


          {/* AUTH MESSAGE */}

          {message && <p>{message}</p>}
        </>
      )}


      {/* =====================================================
          LOGGED-IN USER AREA
      ====================================================== */}

      {user && (
        <>

          {/* =================================================
              USER INFORMATION
          ================================================== */}

          <div>

            <hr />

            <h2>Logged in user</h2>

            <p>
              <strong>ID:</strong> {user.id}
            </p>

            <p>
              <strong>Email:</strong> {user.email}
            </p>

            <p>
              <strong>Role:</strong> {user.role}
            </p>

          </div>


          {/* =================================================
              UPLOAD SECTION
          ================================================== */}

          <div>

            <hr />

            <h2>Upload KYC Document</h2>

            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={(event) => {
                setSelectedFile(
                  event.target.files[0]
                );

                setUploadMessage("");

                // Clear old result when selecting
                // another document
                setSelectedResult(null);
              }}
            />


            <br />
            <br />


            <button
              type="button"
              onClick={handleUpload}
            >
              Upload Document
            </button>


            {/* UPLOAD MESSAGE */}

            {uploadMessage && (
              <p>{uploadMessage}</p>
            )}

          </div>


          {/* =================================================
              DOCUMENT LIST
          ================================================== */}

          <div>

            <hr />

            <h2>My Documents</h2>


            {documents.length === 0 ? (

              <p>
                No documents uploaded yet.
              </p>

            ) : (

              <table
                border="1"
                cellPadding="8"
              >

                <thead>

                  <tr>

                    <th>ID</th>

                    <th>Filename</th>

                    <th>Type</th>

                    <th>Size</th>

                    <th>Status</th>

                    <th>Uploaded</th>

                    <th>Result</th>

                  </tr>

                </thead>


                <tbody>

                  {documents.map((document) => (

                    <tr key={document.id}>

                      <td>
                        {document.id}
                      </td>


                      <td>
                        {document.original_filename}
                      </td>


                      <td>
                        {document.content_type}
                      </td>


                      <td>
                        {document.file_size} bytes
                      </td>


                      <td>
                        {document.status}
                      </td>


                      <td>
                        {new Date(
                          document.created_at
                        ).toLocaleString()}
                      </td>


                      <td>

                        <button
                          type="button"
                          onClick={() =>
                            checkResult(
                              document.id
                            )
                          }
                        >
                          Check Result
                        </button>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            )}

          </div>


          {/* =================================================
              RESULT LOADING
          ================================================== */}

          {resultLoading && (

            <div className="result-card">

              <hr />

              <h2>
                Processing Result
              </h2>

              <p>
                Loading verification result...
              </p>

            </div>

          )}


          {/* =================================================
              VERIFICATION RESULT
          ================================================== */}

          {selectedResult && !resultLoading && (

            <div className="result-card">

              <hr />

              <h2>
                KYC Verification Result
              </h2>


              {/* RESULT DETAILS */}

              <div className="result-grid">


                {/* STATUS */}

                <div>

                  <strong>
                    Status
                  </strong>

                  <p>
                    {selectedResult.status}
                  </p>

                </div>


                {/* DOCUMENT TYPE */}

                <div>

                  <strong>
                    Document Type
                  </strong>

                  <p>
                    {selectedResult.result?.document_type ||
                      "N/A"}
                  </p>

                </div>


                {/* EXTRACTED NAME */}

                <div>

                  <strong>
                    Extracted Name
                  </strong>

                  <p>
                    {selectedResult.result?.extracted_name ||
                      "N/A"}
                  </p>

                </div>


                {/* DOCUMENT NUMBER */}

                <div>

                  <strong>
                    Document Number
                  </strong>

                  <p>
                    {selectedResult.result
                      ?.extracted_document_number ||
                      "N/A"}
                  </p>

                </div>


                {/* DATE OF BIRTH */}

                <div>

                  <strong>
                    Date of Birth
                  </strong>

                  <p>
                    {selectedResult.result
                      ?.date_of_birth ||
                      "N/A"}
                  </p>

                </div>


                {/* CONFIDENCE */}

                <div>

                  <strong>
                    Confidence
                  </strong>

                  <p>
                    {selectedResult.result?.confidence ??
                      0}
                    %
                  </p>

                </div>


                {/* RISK LEVEL */}

                <div>

                  <strong>
                    Risk Level
                  </strong>

                  <p>
                    {selectedResult.result?.risk_level ||
                      "N/A"}
                  </p>

                </div>

              </div>


              {/* =================================================
                  RISK REASONS
              ================================================== */}

              <div className="risk-section">

                <h3>
                  Risk Reasons
                </h3>


                {selectedResult.result
                  ?.risk_reasons?.length > 0 ? (

                  <ul>

                    {selectedResult.result.risk_reasons.map(
                      (reason, index) => (

                        <li key={index}>
                          {reason}
                        </li>

                      )
                    )}

                  </ul>

                ) : (

                  <p>
                    No risk issues detected.
                  </p>

                )}

              </div>

            </div>

          )}


          {/* =================================================
              LOGOUT
          ================================================== */}

          <div>

            <hr />

            <button
              type="button"
              onClick={handleLogout}
            >
              Logout
            </button>

          </div>

        </>
      )}

    </div>
  );
}


export default App;