import React, { useState, useEffect, useRef } from 'react';
import { getChatHistory, addChatMessage } from '../../services/dashboardService';

const ChatPanel = ({ editId }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Reset panel state when editId changes
    setMessages([]);
    setLoading(true);
    
    const fetchChatHistory = async () => {
      try {
        const history = await getChatHistory(editId);
        setMessages(history);
      } catch (error) {
        console.error('Error fetching chat history:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (editId) {
      fetchChatHistory();
    }
  }, [editId]);
  
  // Scroll to the bottom of the chat when messages change
  useEffect(() => {
    // eslint-disable-next-line no-unused-expressions
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (err) {
      return dateString;
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;
    
    const tempMessage = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      user: 'Current User',
      message: newMessage,
      pending: true
    };
    
    setMessages(prev => [...prev, tempMessage]);
    setNewMessage('');
    
    try {
      await addChatMessage(editId, newMessage);
      // Update the temporary message to remove pending status
      setMessages(prev => 
        prev.map(msg => 
          msg.id === tempMessage.id ? { ...msg, pending: false } : msg
        )
      );
    } catch (error) {
      console.error('Error adding message:', error);
      // Mark the message as failed
      setMessages(prev => 
        prev.map(msg => 
          msg.id === tempMessage.id ? { ...msg, pending: false, failed: true } : msg
        )
      );
    }
  };
  
  if (loading) {
    return <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-600"></div>
    </div>;
  }
  
  return (
    <div className="flex flex-col h-[400px]">
      {/* Chat messages area */}
      <div className="flex-1 overflow-y-auto mb-4 bg-gray-100 rounded-md p-3">
        {messages.length === 0 ? (
          <p className="text-center text-gray-600 py-4">No chat history available. Add a note to get started.</p>
        ) : (
          messages.map((msg, index) => (
            <div 
              key={msg.id} 
              className={`mb-3 ${msg.failed ? 'opacity-75' : ''}`}
            >
              <p className="text-xs text-gray-600">
                {msg.user} • {formatDate(msg.timestamp)}
              </p>
              <div 
                className={`mt-1 p-3 rounded-lg shadow-sm ${
                  index % 2 === 0 
                    ? 'bg-indigo-50 border-l-4 border-indigo-500 text-gray-800' 
                    : 'bg-emerald-50 border-l-4 border-emerald-500 text-gray-800'
                }`}
              >
                <p className="text-sm">{msg.message}</p>
                {msg.pending && <span className="text-xs text-amber-600 font-medium">Sending...</span>}
                {msg.failed && <span className="text-xs text-rose-700 font-medium">Failed to send</span>}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Chat input */}
      <form onSubmit={handleSubmit} className="flex">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Add a note or comment..."
          className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          className="bg-indigo-600 text-white px-4 py-2 rounded-r-md hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatPanel; 