import React, { useState } from 'react';
import './App.css';

interface ChatMessage {
  id: number;
  question: string;
  answer: string;
  timestamp: Date;
}

function App() {
  const [, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isPdfLoaded, setIsPdfLoaded] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setIsLoading(true);
      
      try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch('http://localhost:8000/upload-pdf', {
          method: 'POST',
          body: formData,
        });
        
        if (response.ok) {
          setIsPdfLoaded(true);
          alert('PDF uploaded and processed successfully!');
        } else {
          alert('Error uploading PDF');
        }
      } catch (error) {
        alert('Error uploading PDF');
        console.error('Upload error:', error);
      } finally {
        setIsLoading(false);
      }
    } else {
      alert('Please select a PDF file');
    }
  };

  const handleSubmitQuestion = async () => {
    if (!question.trim()) {
      alert('Please enter a question');
      return;
    }

    if (!isPdfLoaded) {
      alert('Please upload a PDF first');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });
      
      if (response.ok) {
        const data = await response.json();
        const newMessage: ChatMessage = {
          id: Date.now(),
          question,
          answer: data.answer,
          timestamp: new Date(),
        };
        
        setChatHistory(prev => [...prev, newMessage]);
        setQuestion('');
      } else {
        alert('Error getting answer');
      }
    } catch (error) {
      alert('Error getting answer');
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📚 PDF Chatbot</h1>
        <p>Upload a PDF and start chatting with it!</p>
      </header>

      <main className="App-main">
        {/* File Upload Section */}
        <div className="upload-section">
          <h2>📄 Upload PDF</h2>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={isLoading}
          />
          {isLoading && <p>Processing PDF...</p>}
          {isPdfLoaded && <p>✅ PDF loaded and ready for questions!</p>}
        </div>

        {/* Chat Section */}
        {isPdfLoaded && (
          <div className="chat-section">
            <h2>💬 Chat with PDF</h2>
            
            {/* Chat History */}
            <div className="chat-history">
              {chatHistory.map((message) => (
                <div key={message.id} className="message">
                  <div className="question">
                    <strong>You:</strong> {message.question}
                  </div>
                  <div className="answer">
                    <strong>PDF:</strong> {message.answer}
                  </div>
                </div>
              ))}
            </div>

            {/* Question Input */}
            <div className="question-input">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about the PDF..."
                disabled={isLoading}
                onKeyPress={(e) => e.key === 'Enter' && handleSubmitQuestion()}
              />
              <button 
                onClick={handleSubmitQuestion}
                disabled={isLoading || !question.trim()}
              >
                {isLoading ? 'Thinking...' : 'Ask'}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;