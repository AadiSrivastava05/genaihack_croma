import React, { useState, useEffect, useCallback } from "react";
import io from "socket.io-client";
import "./PRChatbot.css";

const SOCKET_URL =
  process.env.NODE_ENV === "production"
    ? "https://yourdomain.com"
    : "http://localhost:5005";

const PRChatbot = () => {
  const [prompt, setPrompt] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [socket, setSocket] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const newSocket = io(SOCKET_URL, {
      transports: ["websocket", "polling"],
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 10000,
    });

    newSocket.on("connect", () => {
      console.log("Connected to server");
    });

    newSocket.on("connect_error", (error) => {
      setError("Failed to connect to the server. Please try again later.");
    });

    newSocket.on("disconnect", (reason) => {
      console.log("Disconnected:", reason);
    });

    newSocket.on("chatbot_response", (data) => {
      const newMessage = {
        sender: "Shopkeeper Bot",
        message: data.response,
        productLinks: data.product_links || [],
      };
      setChatMessages((prevMessages) => [...prevMessages, newMessage]);
      setIsLoading(false);
    });

    newSocket.on("chatbot_error", (errorMessage) => {
      setError(errorMessage);
      setIsLoading(false);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const handleSendMessage = useCallback(() => {
    if (prompt.trim() === "") return;

    setIsLoading(true);
    setError(null);

    setChatMessages((prevMessages) => [
      ...prevMessages,
      { sender: "You", message: prompt },
    ]);

    socket.emit("chatbot_message", prompt);

    setPrompt("");
  }, [prompt, socket]);

  const renderMessage = (message) => {
    return message.split("\n").map((line, index) => (
      <React.Fragment key={index}>
        {line}
        <br />
      </React.Fragment>
    ));
  };

  const renderProductLinks = (productLinks) => {
    if (!productLinks.length) return null;

    return (
      <div>
        <strong>Check out these products:</strong>
        {productLinks.map((product, index) => (
          <a
            key={index}
            href={product.link}
            target="_blank"
            rel="noopener noreferrer"
            className="prchatbot-product-link"
          >
            {product.name} {product.sustainability}
          </a>
        ))}
      </div>
    );
  };

  return (
    <div className="prchatbot-app-container">
      <div className="prchatbot-container">
        <div className="prchatbot-header">
          <h1>Chat Assistant</h1>
          <input
            type="text"
            className="prchatbot-search-bar"
            placeholder="Search in chat"
          />
        </div>
        <div
          className="prchatbot-messages"
          style={{ maxHeight: "70vh", overflowY: "auto" }}
        >
          {chatMessages.map((msg, index) => (
            <div
              key={index}
              className={`prchatbot-message ${msg.sender.toLowerCase()}`}
            >
              <strong>{msg.sender}:</strong> {renderMessage(msg.message)}
              {msg.productLinks && renderProductLinks(msg.productLinks)}
            </div>
          ))}
          {error && (
            <div className="prchatbot-error-message">
              {error}
              <button onClick={() => handleSendMessage()}>Retry</button>
            </div>
          )}
        </div>
        <div className="prchatbot-input">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder="Ask a question..."
            disabled={isLoading}
          />
          <button onClick={handleSendMessage} disabled={isLoading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default PRChatbot;
